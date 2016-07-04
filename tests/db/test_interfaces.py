# ------------------------------------------------------------------------------
# FIXME: This is a dummy test case.
# This can be removed when ABCDatabase is used and tested with actual databases
# ------------------------------------------------------------------------------

import unittest
from collections import namedtuple
from remoteappmanager.db.interfaces import ABCDatabase, ApplicationConfig
from .abc_test_interfaces import ABCTestDatabase

User = namedtuple('User', ('name',))


class Database(ABCDatabase):

    def get_user_by_name(self, username):
        return User(name=username)

    def get_apps_for_user(self, username):
        return (ApplicationConfig(mapping_id=username+'1'),
                ApplicationConfig(mapping_id=username+'2'))


class TestDatabase(ABCTestDatabase, unittest.TestCase):
    def setUp(self):
        super().setUp(['foo', 'bar'],
                      [(ApplicationConfig(mapping_id='foo1'),
                        ApplicationConfig(mapping_id='foo2')),
                       (ApplicationConfig(mapping_id='bar1'),
                        ApplicationConfig(mapping_id='bar2'))])

    def create_database(self):
        return Database()

    def test_get_user_by_name(self):
        database = self.create_database()
        self.assertEqual(database.get_user_by_name('foo'), User('foo'))
