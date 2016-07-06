import os
import unittest

from remoteappmanager.db import orm
from remoteappmanager.db.orm import (Database, transaction, Accounting,
                                     AccountingInterface)
from tests.db.abc_test_interfaces import ABCTestDatabaseInterface
from tests.temp_mixin import TempMixin
from tests import utils


def fill_db(session):
    with transaction(session):
        users = [orm.User(name="user"+str(i)) for i in range(5)]
        session.add_all(users)

        # Create a few applications
        apps = [orm.Application(image="docker/image"+str(i))
                for i in range(3)]
        session.add_all(apps)

        policy = orm.ApplicationPolicy(allow_home=False,
                                       allow_common=False,
                                       allow_view=False)
        session.add(policy)

        # We want app 0 to be available only to users 1, 3, and 4
        # app 1 to be available only to user 0
        # and app 2 to be available to user 1

        accountings = [
            orm.Accounting(user=users[1],
                           application=apps[0],
                           application_policy=policy),
            orm.Accounting(user=users[3],
                           application=apps[0],
                           application_policy=policy),
            orm.Accounting(user=users[4],
                           application=apps[0],
                           application_policy=policy),
            orm.Accounting(user=users[0],
                           application=apps[1],
                           application_policy=policy),
            orm.Accounting(user=users[1],
                           application=apps[2],
                           application_policy=policy),
        ]
        session.add_all(accountings)


class TestOrm(TempMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

    def test_database_init_and_session(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        self.assertIsNotNone(session)

    def test_orm_objects(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            users = session.query(orm.User).all()

            # now check if user 1 has access to two accounting entries
            user = users[1]

            res = session.query(Accounting).filter(
                Accounting.user == user).all()

            self.assertEqual(len(res), 2)
            self.assertIn("docker/image0",
                          [acc.application.image for acc in res])
            self.assertIn("docker/image2",
                          [acc.application.image for acc in res])

            # User 2 should have no access to apps
            res = session.query(Accounting).filter(
                Accounting.user == users[2]).all()

            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            res = session.query(Accounting).filter(
                Accounting.user == users[0]).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc.application.image for acc in res])

            # User 3 should have access to app 0 only
            res = session.query(Accounting).filter(
                Accounting.user == users[3]).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc.application.image for acc in res])

    def test_apps_for_user(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            users = session.query(orm.User).all()
            res = orm.apps_for_user(session, users[1])
            self.assertEqual(len(res), 2)
            self.assertIn("docker/image0",
                          [acc[1].image for acc in res])
            self.assertIn("docker/image2",
                          [acc[1].image for acc in res])

            res = orm.apps_for_user(session, users[2])
            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            res = orm.apps_for_user(session, users[0])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc[1].image for acc in res])

            res = orm.apps_for_user(session, users[3])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc[1].image for acc in res])

            res = orm.apps_for_user(session, None)
            self.assertEqual(len(res), 0)

    def test_user_can_run(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            users = session.query(orm.User).all()
            applications = session.query(orm.Application).all()
            policy = session.query(orm.ApplicationPolicy).first()

            self.assertTrue(orm.user_can_run(session,
                                             users[0],
                                             applications[1],
                                             policy))
            self.assertFalse(orm.user_can_run(session,
                                              users[0],
                                              applications[0],
                                              policy))

            self.assertFalse(orm.user_can_run(session,
                                              None,
                                              applications[0],
                                              policy))


class TestOrmInterface(TempMixin, ABCTestDatabaseInterface, unittest.TestCase):
    def setUp(self):
        # Setup temporary directory
        super().setUp()

        # Setup the database
        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

        self.addTypeEqualityFunc(orm.Application, self.assertApplicationEqual)
        self.addTypeEqualityFunc(orm.ApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_expected_users(self):
        return tuple(orm.User(name='user'+str(i)) for i in range(5))

    def create_expected_configs(self, user):
        apps = [orm.Application(image="docker/image"+str(i))
                for i in range(3)]
        policy = orm.ApplicationPolicy(allow_home=False,
                                       allow_common=False,
                                       allow_view=False)
        mappings = {
            'user0': ((apps[1], policy),),
            'user1': ((apps[0], policy),
                      (apps[2], policy)),
            'user2': (()),
            'user3': ((apps[0], policy),),
            'user4': ((apps[0], policy),)}
        return mappings[user.name]

    def create_accounting(self):
        accounting = AccountingInterface(
            url="sqlite:///"+self.sqlite_file_path)

        # Fill the database
        fill_db(accounting.session)

        return accounting

    def test_get_user_by_name(self):
        accounting = self.create_accounting()

        user = accounting.get_user_by_name('user1')
        self.assertIsInstance(user, orm.User)
        self.assertEqual(user.name, 'user1')

        # user not found, result should be None
        user = accounting.get_user_by_name('foo')
        self.assertIsNone(user)
