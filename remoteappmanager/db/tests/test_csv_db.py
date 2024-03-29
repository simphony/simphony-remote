import os
import unittest

from remoteappmanager.db.csv_db import (
    CSVApplication, CSVApplicationPolicy, CSVUser, CSVDatabase)
from remoteappmanager.db.tests.abc_test_interfaces import (
    ABCTestDatabaseInterface)
from remoteappmanager.tests.temp_mixin import TempMixin


class GoodTable:
    headers = ('user.name', 'application.image', 'policy.app_license',
               'policy.allow_home', 'policy.allow_view',
               'policy.allow_common',
               'policy.volume_source', 'policy.volume_target',
               'policy.volume_mode', 'policy.allow_startup_data')

    #    name,    image, home, view, common, source, target, mode, startup_data
    records = [
        ('markdoe', 'simphonyproject/simphony-mayavi:0.6.0', '', '1', '1', '0', '', '', '', '0'),  # noqa
        ('markdoe', 'simphonyproject/ubuntu-image:latest', '', '1', '1', '1', '/src', '/target', 'ro', '0'),  # noqa
        ('johndoe', 'simphonyproject/simphony-mayavi:0.6.0', '', '0', '0', '0', '/src', '/target', 'ro', '0')]  # noqa


class BadTableMissingHeaders:
    # policy.volume_source and policy.volume_target are missing
    headers = ('user.name', 'application.image', 'policy.allow_home',
               'policy.allow_view', 'policy.allow_common',
               'policy.volume_mode', 'policy.allow_startup_data')

    #    name,     image, home, view, common, mode
    records = [
        ('markdoe', 'simphonyproject/simphony-mayavi:0.6.0', '1', '1', '0', '', '0'),  # noqa
        ('markdoe', 'simphonyproject/ubuntu-image:latest', '1', '1', '1', 'ro', '0'),  # noqa
        ('johndoe', 'simphonyproject/simphony-mayavi:0.6.0', '0', '0', '0', 'ro', '0')]  # noqa


class GoodTableWithDifferentHeaders:
    # There is an extra column and the columns order are different
    # but that's okay
    headers = ('policy.app_license', 'policy.allow_view',
               'policy.allow_common',
               'policy.volume_source', 'policy.volume_target',
               'policy.volume_mode',
               'user.name', 'application.image', 'policy.allow_home',
               'policy.allow_startup_data', 'extra_column')

    #  view, common, source, target, mode, name, image, home, extra
    records = [
        ('', '1', '0', '', '', '', 'markdoe', 'simphonyproject/simphony-mayavi:0.6.0', '1', 'anything'),  # noqa
        ('', '1', '1', '/src', '/target', 'ro', '0', 'markdoe', 'simphonyproject/ubuntu-image:latest', '1', '0', 'extra'),  # noqa
        ('', '0', '0', '/src', '/target', 'ro', 'johndoe', 'simphonyproject/simphony-mayavi:0.6.0', '0', '0', 'abc')]  # noqa


def write_csv_file(file_name, headers, records):
    with open(file_name, 'w') as csv_file:
        print(*headers, sep=',', file=csv_file)
        for record in records:
            print(*record, sep=',', file=csv_file)


class TestCSVDatabase(TempMixin, ABCTestDatabaseInterface,
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
        return (CSVUser(0, 'markdoe'), CSVUser(1, 'johndoe'))

    def create_expected_configs(self, user):
        mappings = {
            'markdoe': (
                (CSVApplication(id=0, image='simphonyproject/simphony-mayavi:0.6.0'),  # noqa
                 CSVApplicationPolicy(allow_home=True,
                                      allow_view=True,
                                      allow_common=False,
                                      volume_source=None,
                                      volume_target=None,
                                      volume_mode=None,
                                      allow_startup_data=False)),
                (CSVApplication(id=1, image='simphonyproject/ubuntu-image:latest'),  # noqa
                 CSVApplicationPolicy(allow_home=True,
                                      allow_view=True,
                                      allow_common=True,
                                      volume_source='/src',
                                      volume_target='/target',
                                      volume_mode='ro',
                                      allow_startup_data=False))
                ),
            'johndoe': (
                (CSVApplication(id=0, image='simphonyproject/simphony-mayavi:0.6.0'),  # noqa
                 CSVApplicationPolicy(allow_home=False,
                                      allow_view=False,
                                      allow_common=False,
                                      volume_source='/src',
                                      volume_target='/target',
                                      volume_mode='ro',
                                      allow_startup_data=False)),
                )}
        return mappings[user.name]

    def create_database(self):
        return CSVDatabase(self.csv_file)

    def test_get_user(self):
        database = self.create_database()

        user = database.get_user(user_name='markdoe')
        self.assertIsInstance(user, CSVUser)
        self.assertEqual(user.name, 'markdoe')

        user = database.get_user(id=0)
        self.assertIsInstance(user, CSVUser)
        self.assertEqual(user.name, 'markdoe')

        user = database.get_user(user_name='unknown')
        self.assertIsNone(user)

        with self.assertRaises(ValueError):
            database.get_user(user_name='unknown', id=123)

    def test_error_with_missing_headers(self):
        write_csv_file(self.csv_file,
                       BadTableMissingHeaders.headers,
                       BadTableMissingHeaders.records)

        with self.assertRaisesRegex(ValueError, "Missing headers"):
            self.create_database()

    def test_load_csv_file_with_good_headers_different_order(self):
        """ Test loading a good table with headers of different orders """
        write_csv_file(self.csv_file,
                       GoodTableWithDifferentHeaders.headers,
                       GoodTableWithDifferentHeaders.records)
        self.create_database()
