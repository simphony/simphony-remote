import os
import unittest

from remoteappmanager.db.csv_db import (
    CSVApplication, CSVApplicationPolicy, CSVUser, CSVAccounting)

from tests.db.abc_test_interfaces import ABCTestDatabaseInterface
from tests.temp_mixin import TempMixin


class GoodTable:
    headers = ('user.name', 'application.image', 'policy.allow_home',
               'policy.allow_view', 'policy.allow_common',
               'policy.volume_source', 'policy.volume_target',
               'policy.volume_mode')

    #    name,     image, home, view, common, source, target, mode
    records = [
        ('foo', 'image_1', '1', '1', '0', '', '', ''),
        ('foo', 'image_2', '1', '1', '1', '/src', '/target', 'ro'),
        ('bar', 'image_1', '0', '0', '0', '/src', '/target', 'ro')]


class BadTableMissingHeaders:
    # policy.volume_source and policy.volume_target are missing
    headers = ('user.name', 'application.image', 'policy.allow_home',
               'policy.allow_view', 'policy.allow_common',
               'policy.volume_mode')

    #    name,     image, home, view, common, mode
    records = [
        ('foo', 'image_1', '1', '1', '0', ''),
        ('foo', 'image_2', '1', '1', '1', 'ro'),
        ('bar', 'image_1', '0', '0', '0', 'ro')]


class GoodTableWithDifferentHeaders:
    # There is an extra column and the columns order are different
    # but that's okay
    headers = ('policy.allow_view', 'policy.allow_common',
               'policy.volume_source', 'policy.volume_target',
               'policy.volume_mode',
               'user.name', 'application.image', 'policy.allow_home',
               'extra_column')

    #  view, common, source, target, mode, name, image, home, extra
    records = [
        ('1', '0', '', '', '', 'foo', 'image_1', '1', 'anything'),
        ('1', '1', '/src', '/target', 'ro', 'foo', 'image_2', '1', 'extra'),
        ('0', '0', '/src', '/target', 'ro', 'bar', 'image_1', '0', 'whatever')]


def write_csv_file(file_name, headers, records):
    with open(file_name, 'w') as csv_file:
        print(*headers, sep=',', file=csv_file)
        for record in records:
            print(*record, sep=',', file=csv_file)


class TestCSVAccounting(TempMixin, ABCTestDatabaseInterface,
                        unittest.TestCase):
    def setUp(self):
        # Setup temporary directory
        super().setUp()

        self.csv_file = os.path.join(self.tempdir, 'testing.csv')

        write_csv_file(self.csv_file, GoodTable.headers, GoodTable.records)

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

    def test_error_with_missing_headers(self):
        write_csv_file(self.csv_file,
                       BadTableMissingHeaders.headers,
                       BadTableMissingHeaders.records)

        with self.assertRaisesRegex(ValueError, "Missing headers"):
            self.create_accounting()

    def test_load_csv_file_with_good_headers_different_order(self):
        """ Test loading a good table with headers of different orders """
        write_csv_file(self.csv_file,
                       GoodTableWithDifferentHeaders.headers,
                       GoodTableWithDifferentHeaders.records)
        self.create_accounting()
