import os
import unittest

from remoteappmanager.file_config import FileConfig

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
