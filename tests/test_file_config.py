import os
import unittest

from docker import tls
from remoteappmanager.file_config import FileConfig
from unittest import mock

from tests.temp_mixin import TempMixin


DOCKER_CONFIG = '''
tls = True
tls_verify = True
tls_ca = '~/.docker/machine/machines/default/ca.pem'
tls_cert = '~/.docker/machine/machines/default/cert.pem'
tls_key = '~/.docker/machine/machines/default/key.pem'
docker_host = "tcp://192.168.99.100:2376"
'''

GOOD_ACCOUNTING_CONFIG = '''
accounting_class = "remoteappmanager.db.csv_db.CSVAccounting"
accounting_kwargs = {"csv_file_path": "file_path.csv"}
'''


class TestFileConfig(TempMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()

        # We can run the application config only once. It uses a global
        # object that can't be reinitialized cleanly unless we access a private
        # member.
        self.config_file = os.path.join(self.tempdir,
                                        'config.py')

        self.ca_cert, self.cert_pem, self.key_pem = [
            os.path.join(self.tempdir, x)
            for x in ("ca.cert", "cert.pem", "key.pem")]

        for path in self.ca_cert, self.cert_pem, self.key_pem:
            with open(path, 'w'):
                pass

    def test_initialization_with_default_accounting(self):
        with open(self.config_file, 'w') as fhandle:
            print(DOCKER_CONFIG, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)

    def test_initialization_with_good_accounting(self):
        with open(self.config_file, 'w') as fhandle:
            print(DOCKER_CONFIG, file=fhandle)
            print(GOOD_ACCOUNTING_CONFIG, file=fhandle)

        config = FileConfig()
        config.parse_config(self.config_file)

        self.assertEqual(config.accounting_class,
                         "remoteappmanager.db.csv_db.CSVAccounting")
        self.assertDictEqual(config.accounting_kwargs,
                             {"csv_file_path": "file_path.csv"})

    def test_initialization_on_nonlocal_docker_machine(self):
        ca_cert, cert_pem, key_pem = [
            os.path.join(self.tempdir, x)
            for x in ("ca.cert", "cert.pem", "key.pem")]

        for path in ca_cert, cert_pem, key_pem:
            with open(path, 'w'):
                pass

        with mock.patch("docker.utils.kwargs_from_env") as patched:
            patched.return_value = {
                "base_url": "tcp://192.168.99.100:12345",
                "tls": tls.TLSConfig(
                    client_cert=(self.cert_pem, self.key_pem),
                    ca_cert=self.ca_cert,
                    verify=True,
                    ssl_version="auto",
                    assert_hostname=True)
            }

            config = FileConfig()
            # False by default, as we don't want CA verification
            self.assertEqual(config.tls, False)
            self.assertEqual(config.tls_verify, True)
            self.assertEqual(config.tls_ca, self.ca_cert)
            self.assertEqual(config.tls_cert, self.cert_pem)
            self.assertEqual(config.tls_key, self.key_pem)
            self.assertEqual(config.docker_host, "tcp://192.168.99.100:12345")

        with mock.patch("docker.utils.kwargs_from_env") as patched:
            patched.return_value = {}

            config = FileConfig()
            # False by default, as we don't want CA verification
            self.assertEqual(config.tls, False)
            self.assertEqual(config.tls_verify, False)
            self.assertEqual(config.docker_host, 'unix://var/run/docker.sock')

    def test_overriding(self):
        with mock.patch("docker.utils.kwargs_from_env") as patched:
            patched.return_value = {
                "base_url": "tcp://192.168.99.100:12345",
                "tls": tls.TLSConfig(
                    client_cert=(self.cert_pem, self.key_pem),
                    ca_cert=self.ca_cert,
                    verify=True,
                    ssl_version="auto",
                    assert_hostname=True)
            }

            config = FileConfig()
            config.tls_verify = False
            config.docker_host = "tcp://192.168.99.100:31337"
            # False by default, as we don't want CA verification
            docker_config = config.docker_config()
            self.assertNotIn("tls", docker_config)
            self.assertEqual(docker_config["base_url"],
                             "tcp://192.168.99.100:31337")
