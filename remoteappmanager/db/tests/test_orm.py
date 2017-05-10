import contextlib
import uuid
import os

from tornado.testing import LogTrapTestCase

from remoteappmanager.db import orm
from remoteappmanager.db import exceptions
from remoteappmanager.db.orm import (Database, transaction, Accounting,
                                     ORMDatabase)
from remoteappmanager.db.tests.abc_test_interfaces import (
    ABCTestDatabaseInterface)
from remoteappmanager.tests import utils
from remoteappmanager.tests.temp_mixin import TempMixin


def fill_db(session):
    with transaction(session):
        users = [orm.User(name="user"+str(i)) for i in range(5)]
        session.add_all(users)

        # Create a few applications
        images = [orm.Image(name="docker/image"+str(i)) for i in range(3)]
        session.add_all(images)

        policy = orm.ApplicationPolicy(allow_home=False,
                                       allow_common=False,
                                       allow_view=False)
        session.add(policy)

        # We want app 0 to be available only to users 1, 3, and 4
        # app 1 to be available only to user 0
        # and app 2 to be available to user 1

        accountings = []

        for user, image in [
                (users[1], images[0]),
                (users[3], images[0]),
                (users[4], images[0]),
                (users[0], images[1]),
                (users[1], images[2])]:

            id = uuid.uuid4().hex

            accountings.append(
                orm.Accounting(id=id,
                               user=user,
                               image=image,
                               application_policy=policy)
            )

        session.add_all(accountings)


class TestOrm(TempMixin, LogTrapTestCase):
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
                          [acc.image.name for acc in res])
            self.assertIn("docker/image2",
                          [acc.image.name for acc in res])

            # User 2 should have no access to apps
            res = session.query(Accounting).filter(
                Accounting.user == users[2]).all()

            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            res = session.query(Accounting).filter(
                Accounting.user == users[0]).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc.image.name for acc in res])

            # User 3 should have access to app 0 only
            res = session.query(Accounting).filter(
                Accounting.user == users[3]).all()

            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc.image.name for acc in res])

    def test_accounting_for_user(self):
        db = Database(url="sqlite:///"+self.sqlite_file_path)
        session = db.create_session()
        fill_db(session)
        with transaction(session):
            # verify back population
            users = session.query(orm.User).all()
            res = orm.accounting_for_user(session, users[1])
            self.assertEqual(len(res), 2)
            self.assertIn("docker/image0",
                          [acc.image.name for acc in res])
            self.assertIn("docker/image2",
                          [acc.image.name for acc in res])

            res = orm.accounting_for_user(session, users[2])
            self.assertEqual(len(res), 0)

            # User 0 should have access to app 1
            res = orm.accounting_for_user(session, users[0])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image1",
                          [acc.image.name for acc in res])

            res = orm.accounting_for_user(session, users[3])
            self.assertEqual(len(res), 1)
            self.assertIn("docker/image0",
                          [acc.image.name for acc in res])

            res = orm.accounting_for_user(session, None)
            self.assertEqual(len(res), 0)


class TestOrmDatabase(TempMixin, ABCTestDatabaseInterface,
                      LogTrapTestCase):
    def setUp(self):
        # Setup temporary directory
        super().setUp()

        # Setup the database
        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

        self.addTypeEqualityFunc(orm.Image, self.assertImageEqual)
        self.addTypeEqualityFunc(orm.ApplicationPolicy,
                                 self.assertApplicationPolicyEqual)

    def create_expected_users(self):
        return tuple(orm.User(name='user'+str(i)) for i in range(5))

    def create_expected_configs(self, user):
        apps = [orm.Image(name="docker/image"+str(i)) for i in range(3)]
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

    def create_database(self):
        database = ORMDatabase(
            url="sqlite:///"+self.sqlite_file_path)

        # Fill the database
        with contextlib.closing(database.db.create_session()) as session:
            fill_db(session)

        return database

    def test_get_user(self):
        database = self.create_database()

        user = database.get_user(user_name='user1')
        self.assertIsInstance(user, orm.User)

        user = database.get_user(id=1)
        self.assertIsInstance(user, orm.User)

        # user not found, result should be None
        user = database.get_user(user_name='foo')
        self.assertIsNone(user)

        user = database.get_user(id=124)
        self.assertIsNone(user)

        with self.assertRaises(ValueError):
            database.get_user(id=1, user_name="foo")

    def test_get_accounting_for_user_across_sessions(self):
        database = self.create_database()

        # user is retrieved from one session
        user = database.get_user(user_name='user1')

        # apps is retrieved from another sessions
        accounting = database.get_accounting_for_user(user)[0]

        expected_config = self.create_expected_configs(orm.User(name='user1'))

        self.assertEqual(accounting.image, expected_config[0][0])
        self.assertEqual(accounting.application_policy, expected_config[0][1])

    def test_no_file_creation_if_sqlite_database_not_exist(self):
        temp_file_path = os.path.join(self.tempdir, 'some.db')

        with self.assertRaises(IOError):
            ORMDatabase(
                url="sqlite:///"+temp_file_path)

        self.assertFalse(os.path.exists(temp_file_path))

    def test_create_user(self):
        database = self.create_database()
        prev_length = len(database.list_users())

        id = database.create_user("ciccio")

        user = database.get_user(user_name="ciccio")
        self.assertIsNotNone(user)
        self.assertIsNotNone(id)
        self.assertEqual(len(database.list_users()), prev_length + 1)

        with self.assertRaises(exceptions.Exists):
            database.create_user("ciccio")

    def test_remove_user_by_name(self):
        database = self.create_database()
        prev_length = len(database.list_users())

        database.remove_user(user_name="user1")

        self.assertIsNone(database.get_user(user_name="ciccio"))
        self.assertEqual(len(database.list_users()), prev_length - 1)

        # This should be neutral
        database.remove_user(user_name="user1")

    def test_remove_user_by_id(self):
        database = self.create_database()
        user = database.get_user(user_name="user1")
        id = user.id
        prev_length = len(database.list_users())

        database.remove_user(id=id)
        self.assertIsNone(database.get_user(user_name="user1"))
        self.assertEqual(len(database.list_users()), prev_length - 1)

        # This should be neutral
        database.remove_user(id=id)

    def test_remove_user_one_arg(self):
        database = self.create_database()

        with self.assertRaises(ValueError):
            database.remove_user(user_name="foo", id=3)

        with self.assertRaises(ValueError):
            database.remove_user()

    def test_create_image(self):
        database = self.create_database()
        prev_length = len(database.list_images())

        id = database.create_image("simphonyremote/amazing")
        self.assertIsNotNone(id)
        app_list = database.list_images()
        self.assertEqual(len(app_list), prev_length + 1)

        apps = [a for a in app_list if a.id == id]
        self.assertEqual(len(apps), 1)

        with self.assertRaises(exceptions.Exists):
            database.create_image("simphonyremote/amazing")

    def test_remove_image(self):
        database = self.create_database()
        prev_length = len(database.list_images())

        database.remove_image(name="docker/image0")

        self.assertEqual(len(database.list_images()), prev_length - 1)

        # This should be neutral
        database.remove_image(name="docker/image0")

    def test_remove_image_by_id(self):
        database = self.create_database()
        app_list = database.list_images()
        id = app_list[0].id
        prev_length = len(app_list)

        database.remove_image(id=id)

        self.assertEqual(len(database.list_images()), prev_length - 1)

        # This should be neutral
        database.remove_image(id=id)

    def test_remove_image_one_arg(self):
        database = self.create_database()

        with self.assertRaises(ValueError):
            database.remove_image(name="foo", id=3)

        with self.assertRaises(ValueError):
            database.remove_image()

    def test_grant_revoke_access(self):
        database = self.create_database()

        with self.assertRaises(exceptions.NotFound):
            database.grant_access("simphonyremote/amazing", "ciccio",
                                  True, False, "/foo:/bar:ro")
        database.create_user("ciccio")

        with self.assertRaises(exceptions.NotFound):
            database.grant_access("simphonyremote/amazing", "ciccio",
                                  True, False, "/foo:/bar:ro")

        database.create_image("simphonyremote/amazing")

        id = database.grant_access("simphonyremote/amazing", "ciccio",
                                   True, False, "/foo:/bar:ro")
        self.assertIsNotNone(id)

        user = database.get_user(user_name="ciccio")
        acc = database.get_accounting_for_user(user)
        self.assertEqual(acc[0].id, id)
        self.assertEqual(acc[0].image.name, "simphonyremote/amazing")
        self.assertEqual(acc[0].application_policy.allow_home, True)
        self.assertEqual(acc[0].application_policy.allow_view, False)
        self.assertEqual(acc[0].application_policy.volume_source, "/foo")
        self.assertEqual(acc[0].application_policy.volume_target, "/bar")
        self.assertEqual(acc[0].application_policy.volume_mode, "ro")

        # Do it twice to check idempotency
        id2 = database.grant_access("simphonyremote/amazing", "ciccio",
                                    True, False, "/foo:/bar:ro")
        self.assertEqual(id, id2)

        database.revoke_access("simphonyremote/amazing", "ciccio",
                               True, False, "/foo:/bar:ro")

        self.assertEqual(len(database.get_accounting_for_user(user)), 0)

        with self.assertRaises(exceptions.NotFound):
            database.revoke_access("simphonyremote/amazing", "hello",
                                   True, False, "/foo:/bar:ro")

    def test_grant_revoke_access_volume(self):
        database = self.create_database()

        database.create_user("ciccio")
        database.create_image("simphonyremote/amazing")
        database.grant_access("simphonyremote/amazing", "ciccio",
                              True, False, None)

        user = database.get_user(user_name="ciccio")
        acc = database.get_accounting_for_user(user)
        self.assertEqual(acc[0].image.name, "simphonyremote/amazing")
        self.assertEqual(acc[0].application_policy.allow_home, True)
        self.assertEqual(acc[0].application_policy.allow_view, False)
        self.assertEqual(acc[0].application_policy.volume_source, None)
        self.assertEqual(acc[0].application_policy.volume_target, None)
        self.assertEqual(acc[0].application_policy.volume_mode, None)

        database.revoke_access("simphonyremote/amazing", "ciccio",
                               True, False, None)

        self.assertEqual(len(database.get_accounting_for_user(user)), 0)

    def test_revoke_by_id(self):
        database = self.create_database()

        database.create_user("ciccio")
        database.create_image("simphonyremote/amazing")
        id = database.grant_access("simphonyremote/amazing", "ciccio",
                                   True, False, None)

        user = database.get_user(user_name="ciccio")
        apps = database.get_accounting_for_user(user)
        self.assertEqual(len(apps), 1)
        self.assertIsNotNone(id)

        database.revoke_access_by_id(id)
        user = database.get_user(user_name="ciccio")
        apps = database.get_accounting_for_user(user)
        self.assertEqual(len(apps), 0)

        # Id not present, should do nothing
        database.revoke_access_by_id(3441)

    def test_unsupported_ops(self):
        """Override to silence the base class assumption that most of
        our backends are unable to create."""
        pass
