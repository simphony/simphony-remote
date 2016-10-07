import contextlib
import os
import unittest

from remoteappmanager.db import orm
from remoteappmanager.db import exceptions
from remoteappmanager.db.orm import (Database, transaction, Accounting,
                                     AppAccounting)
from remoteappmanager.db.tests.abc_test_interfaces import (
    ABCTestDatabaseInterface)
from remoteappmanager.tests import utils
from remoteappmanager.tests.temp_mixin import TempMixin


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


class TestOrmAppAccounting(TempMixin, ABCTestDatabaseInterface,
                           unittest.TestCase):
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
        accounting = AppAccounting(
            url="sqlite:///"+self.sqlite_file_path)

        # Fill the database
        with contextlib.closing(accounting.db.create_session()) as session:
            fill_db(session)

        return accounting

    def test_get_user_by_name(self):
        accounting = self.create_accounting()

        user = accounting.get_user_by_name('user1')
        self.assertIsInstance(user, orm.User)

        # user not found, result should be None
        user = accounting.get_user_by_name('foo')
        self.assertIsNone(user)

    def test_get_apps_for_user_across_sessions(self):
        accounting = self.create_accounting()

        # user is retrieved from one session
        user = accounting.get_user_by_name('user1')

        # apps is retrieved from another sessions
        actual_app, actual_policy = accounting.get_apps_for_user(user)[0][1:]

        expected_config = self.create_expected_configs(orm.User(name='user1'))

        self.assertEqual(actual_app, expected_config[0][0])
        self.assertEqual(actual_policy, expected_config[0][1])

    def test_no_file_creation_if_sqlite_database_not_exist(self):
        temp_file_path = os.path.join(self.tempdir, 'some.db')

        with self.assertRaises(IOError):
            AppAccounting(
                url="sqlite:///"+temp_file_path)

        self.assertFalse(os.path.exists(temp_file_path))

    def test_create_user(self):
        accounting = self.create_accounting()
        prev_length = len(accounting.list_users())

        accounting.create_user("ciccio")
        self.assertIsNotNone(accounting.get_user_by_name("ciccio"))
        self.assertEqual(len(accounting.list_users()), prev_length + 1)

        with self.assertRaises(exceptions.Exists):
            accounting.create_user("ciccio")

    def test_remove_user(self):
        accounting = self.create_accounting()
        prev_length = len(accounting.list_users())

        accounting.remove_user("user1")

        self.assertIsNone(accounting.get_user_by_name("ciccio"))
        self.assertEqual(len(accounting.list_users()), prev_length - 1)

    def test_create_application(self):
        accounting = self.create_accounting()
        prev_length = len(accounting.list_applications())

        accounting.create_application("simphonyremote/amazing")
        self.assertEqual(len(accounting.list_applications()), prev_length + 1)

        with self.assertRaises(exceptions.Exists):
            accounting.create_application("simphonyremote/amazing")

    def test_remove_application(self):
        accounting = self.create_accounting()
        prev_length = len(accounting.list_applications())

        accounting.remove_application("docker/image0")

        self.assertEqual(len(accounting.list_applications()), prev_length - 1)

        with self.assertRaises(exceptions.NotFound):
            accounting.remove_application("docker/image0")

    def test_grant_revoke_access(self):
        accounting = self.create_accounting()

        accounting.create_user("ciccio")
        accounting.create_application("simphonyremote/amazing")
        accounting.grant_access("simphonyremote/amazing", "ciccio",
                                True, False, "/foo:/bar:ro")

        user = accounting.get_user_by_name("ciccio")
        apps = accounting.get_apps_for_user(user)
        self.assertEqual(apps[0][1].image, "simphonyremote/amazing")
        self.assertEqual(apps[0][2].allow_home, True)
        self.assertEqual(apps[0][2].allow_view, False)
        self.assertEqual(apps[0][2].volume_source, "/foo")
        self.assertEqual(apps[0][2].volume_target, "/bar")
        self.assertEqual(apps[0][2].volume_mode, "ro")

        accounting.revoke_access("simphonyremote/amazing", "ciccio",
                                 True, False, "/foo:/bar:ro")

        self.assertEqual(len(accounting.get_apps_for_user(user)), 0)

        with self.assertRaises(exceptions.NotFound):
            accounting.revoke_access("simphonyremote/amazing", "hello",
                                     True, False, "/foo:/bar:ro")
