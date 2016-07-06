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
        super().setUp([User('foo'), User('bar')],
                      [(
                          (Application(image='foo1'), ApplicationPolicy()),
                          (Application(image='foo2'), ApplicationPolicy())
                      ),
                       (
                           (Application(image='bar1'), ApplicationPolicy()),
                           (Application(image='bar2'), ApplicationPolicy())
                       )])

        self.addTypeEqualityFunc(Application,
                                 self.assertApplicationEqual)
        self.addTypeEqualityFunc(ApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_accounting(self):
        return Accounting()

    def test_get_user_by_name(self):
        database = self.create_accounting()
        self.assertEqual(database.get_user_by_name('foo'), User('foo'))
