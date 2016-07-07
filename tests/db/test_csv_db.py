import os
import unittest

from remoteappmanager.db.csv_db import (
    CSVApplication, CSVApplicationPolicy, CSVUser, CSVAccounting)

from tests.db.abc_test_interfaces import ABCTestDatabaseInterface
from tests.temp_mixin import TempMixin


def write_csv_file(file_name):
    _HEADERS = ('user.name', 'application.image', 'policy.allow_home',
                'policy.allow_view', 'policy.allow_common',
                'policy.volume_source', 'policy.volume_target',
                'policy.volume_mode')

    #    name,     image, home, view, common, source, target, mode
    _RECORDS = [
        ('foo', 'image_1', '1', '1', '0', '', '', ''),
        ('foo', 'image_2', '1', '1', '1', '/src', '/target', 'ro'),
        ('bar', 'image_1', '0', '0', '0', '/src', '/target', 'ro')]

    with open(file_name, 'w') as csv_file:
        print(*_HEADERS, sep=',', file=csv_file)
        for record in _RECORDS:
            print(*record, sep=',', file=csv_file)


class TestCSVAccounting(TempMixin, ABCTestDatabaseInterface,
                        unittest.TestCase):
    def setUp(self):
        # Setup temporary directory
        super().setUp()

        self.csv_file = os.path.join(self.tempdir, 'testing.csv')

        write_csv_file(self.csv_file)

        self.addTypeEqualityFunc(CSVApplication, self.assertApplicationEqual)
        self.addTypeEqualityFunc(CSVApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_expected_users(self):
        return (CSVUser('foo'), CSVUser('bar'))

    def create_expected_configs(self, user):
        mappings = {
            'foo': (
                (CSVApplication(image='image_1'),
                 CSVApplicationPolicy(allow_home=True,
                                      allow_view=True,
                                      allow_common=False,
                                      volume_source=None,
                                      volume_target=None,
                                      volume_mode=None)),
                (CSVApplication(image='image_2'),
                 CSVApplicationPolicy(allow_home=True,
                                      allow_view=True,
                                      allow_common=True,
                                      volume_source='/src',
                                      volume_target='/target',
                                      volume_mode='ro'))
                ),
            'bar': (
                (CSVApplication(image='image_1'),
                 CSVApplicationPolicy(allow_home=False,
                                      allow_view=False,
                                      allow_common=False,
                                      volume_source='/src',
                                      volume_target='/target',
                                      volume_mode='ro')),
                )}
        return mappings[user.name]

    def create_accounting(self):
        return CSVAccounting(self.csv_file)

    def test_get_user_by_name(self):
        accounting = self.create_accounting()

        user = accounting.get_user_by_name('foo')
        self.assertIsInstance(user, CSVUser)
        self.assertEqual(user.name, 'foo')

        user = accounting.get_user_by_name('unknown')
        self.assertIsNone(user)
