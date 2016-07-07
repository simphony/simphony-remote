# ------------------------------------------------------------------------------
# FIXME: This is a dummy test case.
# This can be removed when ABCDatabase is used and tested with actual databases
# ------------------------------------------------------------------------------

import unittest
from collections import namedtuple

from remoteappmanager.db.interfaces import (
    ABCApplication, ABCApplicationPolicy, ABCAccounting)
from .abc_test_interfaces import ABCTestDatabaseInterface

User = namedtuple('User', ('name',))


class Application(ABCApplication):
    pass


class ApplicationPolicy(ABCApplicationPolicy):
    pass


class Accounting(ABCAccounting):

    def get_user_by_name(self, username):
        return User(name=username)

    def get_apps_for_user(self, user):
        return (('mapping_id1',
                 Application(image=user.name+'1'), ApplicationPolicy()),
                ('mapping_id2',
                 Application(image=user.name+'2'), ApplicationPolicy()))


class TestDatabaseInterface(ABCTestDatabaseInterface, unittest.TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Application,
                                 self.assertApplicationEqual)
        self.addTypeEqualityFunc(ApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_expected_users(self):
        return [User('foo'), User('bar')]

    def create_expected_configs(self, user):
        return [(Application(image=user.name+'1'), ApplicationPolicy()),
                (Application(image=user.name+'2'), ApplicationPolicy())]

    def create_accounting(self):
        return Accounting()

    def test_get_user_by_name(self):
        database = self.create_accounting()
        self.assertEqual(database.get_user_by_name('foo'), User('foo'))
