import os
import contextlib
import unittest
import textwrap

import docker

from remoteappmanager.file_config import FileConfig

from remoteappmanager.tests.temp_mixin import TempMixin


DOCKER_CONFIG = '''
tls = True
tls_verify = True
tls_ca = '~/.docker/machine/machines/default/ca.pem'
tls_cert = '~/.docker/machine/machines/default/cert.pem'
tls_key = '~/.docker/machine/machines/default/key.pem'
docker_host = "tcp://192.168.99.100:2376"
docker_realm = "myrealm"
'''

GOOD_ACCOUNTING_CONFIG = '''
database_class = "remoteappmanager.db.csv_db.CSVDatabase"
database_kwargs = {"csv_file_path": "file_path.csv"}
'''

GA_TRACKING = '''
ga_tracking_id = "UA-12345-6"
'''


@contextlib.contextmanager
def envvars(envs):
    """Replaces some envvars and restores the old values when done."""
    old_env = {}
    for var, value in envs.items():
        old_env[var] = os.environ.get(var)
        os.environ[var] = value

    yield

    for var in envs:
        if old_env[var] is None:
            del os.environ[var]
        else:
            os.environ[var] = old_env[var]


class TestFileConfig(TempMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()

        # We can run the application config only once. It uses a global
        # object that can't be reinitialized cleanly unless we access a private
        # member.
        self.config_file = os.path.join(self.tempdir,
                                        'config.py')

        # Create dummy certfiles
        for file in ["ca.pem", "cert.pem", "key.pem"]:
            with open(os.path.join(self.tempdir, file), "w"):
                pass

    def test_initialization_with_default_accounting(self):
        with open(self.config_file, 'w') as fhandle:
            print(DOCKER_CONFIG, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)

        self.assertEqual(config.docker_host, "https://192.168.99.100:2376")
        self.assertEqual(config.docker_realm, "myrealm")

    def test_tls_no_verify(self):
        docker_config_tls = textwrap.dedent('''
        tls = True
        tls_verify = False
        tls_cert = '{}'
        tls_key = '{}'
        docker_host = "tcp://192.168.99.100:2376"
        '''.format(
            os.path.join(self.tempdir, "cert.pem"),
            os.path.join(self.tempdir, "key.pem")))

        with open(self.config_file, 'w') as fhandle:
            print(docker_config_tls, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)
        docker_dict = config.docker_config()
        self.assertIn("tls", docker_dict)
        self.assertEqual(docker_dict["tls"].verify, False)
        self.assertEqual(docker_dict["tls"].ca_cert, None)

    def test_initialization_with_good_accounting(self):
        with open(self.config_file, 'w') as fhandle:
            print(DOCKER_CONFIG, file=fhandle)
            print(GOOD_ACCOUNTING_CONFIG, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)

        self.assertEqual(config.database_class,
                         "remoteappmanager.db.csv_db.CSVDatabase")
        self.assertDictEqual(config.database_kwargs,
                             {"csv_file_path": "file_path.csv"})

    def test_initialization_on_nonlocal_docker_machine(self):
        envs = {"DOCKER_HOST": "tcp://192.168.99.100:12345",
                "DOCKER_TLS_VERIFY": "1",
                "DOCKER_CERT_PATH": self.tempdir}

        with envvars(envs):
            config = FileConfig()
            self.assertEqual(config.tls, True)
            self.assertEqual(config.tls_verify, True)
            self.assertEqual(config.tls_ca,
                             os.path.join(self.tempdir, "ca.pem"))
            self.assertEqual(config.tls_cert,
                             os.path.join(self.tempdir, "cert.pem"))
            self.assertEqual(config.tls_key,
                             os.path.join(self.tempdir, "key.pem"))
            self.assertEqual(config.docker_host,
                             "https://192.168.99.100:12345")
            docker_conf = config.docker_config()
            self.assertIn("tls", docker_conf)
            self.assertEqual(docker_conf["tls"].verify, True)
            self.assertEqual(docker_conf["tls"].ca_cert,
                             os.path.join(self.tempdir, "ca.pem"))

    def test_initialization_on_local_docker_machine(self):
        envs = {"DOCKER_HOST": "",
                "DOCKER_TLS_VERIFY": "",
                "DOCKER_CERT_PATH": ""}
        with envvars(envs):
            config = FileConfig()
            # False by default, as we don't want CA verification
            self.assertEqual(config.tls, False)
            self.assertEqual(config.tls_verify, False)
            self.assertEqual(config.docker_host, 'unix://var/run/docker.sock')

    def test_overriding(self):
        envs = {"DOCKER_HOST": "tcp://192.168.99.100:12345",
                "DOCKER_TLS_VERIFY": "1",
                "DOCKER_CERT_PATH": self.tempdir}

        with envvars(envs):
            config = FileConfig()
            config.tls = False
            config.tls_verify = False
            config.docker_host = "tcp://192.168.99.100:31337"
            docker_config = config.docker_config()
            self.assertNotIn("tls", docker_config)
            self.assertEqual(docker_config["base_url"],
                             "tcp://192.168.99.100:31337")

    def test_tls_init(self):
        config = FileConfig(tls=True)
        self.assertNotEqual(config.tls_key, '')
        self.assertNotEqual(config.tls_cert, '')

    def test_ga_tracking(self):
        with open(self.config_file, 'w') as fhandle:
            print(GA_TRACKING, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)

        self.assertEqual(config.ga_tracking_id, 'UA-12345-6')

    def test_file_parsing_not_overriding_bug_131(self):
        docker_config = textwrap.dedent('''
            tls = True
            ''')
        with open(self.config_file, 'w') as fhandle:
            print(docker_config, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)
        self.assertNotEqual(config.tls_key, '')
        self.assertNotEqual(config.tls_cert, '')

    def test_if_docker_config_result_is_acceptable_for_dockerpy(self):
        config = FileConfig()
        docker_config = config.docker_config()

        with contextlib.closing(docker.APIClient(**docker_config)) as client:
            self.assertIsNotNone(client.info())
