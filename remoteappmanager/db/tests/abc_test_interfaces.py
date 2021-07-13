from abc import abstractmethod, ABCMeta
import inspect as _inspect
import string

from remoteappmanager.db.interfaces import ABCApplication, ABCApplicationPolicy
from remoteappmanager.db import exceptions


class ABCTestDatabaseInterface(metaclass=ABCMeta):
    def assertApplicationEqual(self, app1, app2, msg=None):
        args = _inspect.getargs(ABCApplication.__init__.__code__).args[1:]
        for arg in args:
            if arg == 'id':
                # Skip the id because our comparison objects may not have them.
                continue

            if getattr(app1, arg) != getattr(app2, arg):
                raise self.failureException(msg)

    def assertApplicationPolicyEqual(self, policy1, policy2, msg=None):
        args = _inspect.getargs(
            ABCApplicationPolicy.__init__.__code__).args[1:]
        for arg in args:
            if getattr(policy1, arg) != getattr(policy2, arg):
                raise self.failureException(msg)

    @abstractmethod
    def create_expected_users(self):
        """ Return a list of expected users """

    @abstractmethod
    def create_expected_configs(self, user):
        """ Return a list of (Application, ApplicationPolicy) pair for
        the given user.
        """

    @abstractmethod
    def create_database(self):
        """ Create an object that complies with ABCAccounting """

    @abstractmethod
    def test_get_user(self):
        """ Test ABCDatabase.get_user """

    def test_get_accounting_for_user(self):
        """ Test get_accounting_for_user returns an iterable of ApplicationConfig
        """
        database = self.create_database()

        self.assertEqual(database.get_accounting_for_user(None), [])

        for user in self.create_expected_users():
            expected_configs = self.create_expected_configs(user)

            actual_id_configs = database.get_accounting_for_user(user)

            # should be ( (Application, ApplicationPolicy),
            #             (Application, ApplicationPolicy) ... )
            actual_configs = tuple((accounting.application,
                                    accounting.application_policy)
                                   for accounting in actual_id_configs)

            # Compare the content of list of (Application, ApplicationPolicy)
            # Note that their order does not matter
            self.assertEqual(len(actual_configs), len(expected_configs),
                             "Expected: {}, Actual: {}".format(
                                 expected_configs, actual_configs))

            temp = list(actual_configs)
            for expected in expected_configs:
                for index, actual in enumerate(temp[:]):
                    try:
                        self.assertEqual(actual[0], expected[0])
                        self.assertEqual(actual[1], expected[1])
                    except AssertionError:
                        continue
                    else:
                        temp.pop(index)
                        break
                else:
                    self.fail('Expected {0} is not found in {1}'.format(
                        expected, actual_configs))

            if temp:
                self.fail('These are not expected: {}'.format(temp))

    def test_get_accounting_for_user_mapping_id_rest_compliant(self):
        ''' Test if the mapping_id to be rest identifier complient '''
        allowed_chars = set(string.ascii_letters+string.digits)
        database = self.create_database()

        for user in self.create_expected_users():
            # should be ((mapping_id, Application, ApplicationPolicy),
            #            (mapping_id, Application, ApplicationPolicy) ... )
            actual_id_configs = database.get_accounting_for_user(user)

            if not actual_id_configs:
                continue

            for entry in actual_id_configs:
                self.assertFalse(
                    set(entry.id) - allowed_chars,
                    "mapping id should contain these characters only: {} "
                    "Got : {}".format(allowed_chars, entry.id))

    def test_list_users(self):
        database = self.create_database()

        expected_names = sorted([user.name
                                 for user in self.create_expected_users()])
        obtained_names = sorted([user.name
                                 for user in database.list_users()])
        self.assertEqual(expected_names, obtained_names)

    def test_list_applications(self):
        database = self.create_database()

        expected_images = set()
        for user in self.create_expected_users():
            expected_images.update(
                set([app.image
                     for app, _ in self.create_expected_configs(user)])
            )

        obtained_images = set(
            [app.image for app in database.list_applications()]
        )

        self.assertEqual(expected_images, obtained_images)

    def test_unsupported_ops(self):
        db = self.create_database()

        for method in [db.create_user,
                       db.create_application,
                       ]:
            with self.assertRaises(exceptions.UnsupportedOperation):
                method("bonkers")

        for method in [db.remove_user,
                       db.remove_application
                       ]:
            with self.assertRaises(exceptions.UnsupportedOperation):
                method(id=12345)

        for method in [db.grant_access, db.revoke_access]:
            with self.assertRaises(exceptions.UnsupportedOperation):
                method("bonkers", "uuu", 'key', True, False, "/a:/b:ro")

        with self.assertRaises(exceptions.UnsupportedOperation):
            db.revoke_access_by_id(12345)
