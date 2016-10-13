# ------------------------------------------------------------------------------
# FIXME: This is a dummy test case.
# This can be removed when ABCDatabase is used and tested with actual databases
# ------------------------------------------------------------------------------


import unittest
from collections import namedtuple

from remoteappmanager.db.interfaces import (
    ABCApplication, ABCApplicationPolicy, ABCAccounting)
from remoteappmanager.db import exceptions
from remoteappmanager.db.tests.abc_test_interfaces import (
    ABCTestDatabaseInterface)

User = namedtuple('User', ('id', 'name'))


class Application(ABCApplication):
    pass


class ApplicationPolicy(ABCApplicationPolicy):
    pass


class Accounting(ABCAccounting):

    def get_user(self, *, user_name=None, id=None):
        return User(id=0, name=user_name)

    def get_apps_for_user(self, user):
        return (('abc1',
                 Application(id=0, image=user.name+'1'), ApplicationPolicy()),
                ('abc2',
                 Application(id=1, image=user.name+'2'), ApplicationPolicy()))

    def create_user(self, user_name):
        raise exceptions.UnsupportedOperation()

    def remove_user(self, *, user_name=None, id=None):
        raise exceptions.UnsupportedOperation()

    def list_users(self):
        return [User(0, 'foo'), User(1, 'bar')]

    def create_application(self, app_name):
        raise exceptions.UnsupportedOperation()

    def remove_application(self, *, app_name=None, id=None):
        raise exceptions.UnsupportedOperation()

    def list_applications(self):
        return [Application(id=0, image="foo1"),
                Application(id=1, image="foo2"),
                Application(id=2, image="bar1"),
                Application(id=3, image="bar2")
                ]

    def grant_access(self, app_name, user_name,
                     allow_home, allow_view, volume):
        raise exceptions.UnsupportedOperation()

    def revoke_access(self, app_name, user_name,
                      allow_home, allow_view, volume):
        raise exceptions.UnsupportedOperation()


class TestDatabaseInterface(ABCTestDatabaseInterface, unittest.TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Application,
                                 self.assertApplicationEqual)
        self.addTypeEqualityFunc(ApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_expected_users(self):
        return [User(0, 'foo'), User(1, 'bar')]

    def create_expected_configs(self, user):
        return [(Application(id=0, image=user.name+'1'), ApplicationPolicy()),
                (Application(id=1, image=user.name+'2'), ApplicationPolicy())]

    def create_accounting(self):
        return Accounting()

    def test_get_user(self):
        database = self.create_accounting()
        self.assertEqual(database.get_user(user_name='foo'), User(0, 'foo'))
