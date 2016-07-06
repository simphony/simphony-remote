from abc import abstractmethod, ABCMeta
from collections import Iterable
import inspect as _inspect

from remoteappmanager.db.interfaces import ABCApplication, ABCApplicationPolicy


class ABCTestDatabaseInterface(metaclass=ABCMeta):

    def assertApplicationEqual(self, app1, app2, msg=None):
        args = _inspect.getargs(ABCApplication.__init__.__code__).args[1:]
        for arg in args:
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
    def create_accounting(self):
        """ Create an object that complies with ABCAccounting """

    @abstractmethod
    def test_get_user_by_name(self):
        """ Test ABCDatabase.get_user_by_name """

    def test_get_apps_for_user(self):
        """ Test get_apps_for_user returns an iterable of ApplicationConfig
        """
        accounting = self.create_accounting()

        for user in self.create_expected_users():
            expected_configs = self.create_expected_configs(user)

            # should be ((mapping_id, Application, ApplicationPolicy),
            #            (mapping_id, Application, ApplicationPolicy) ... )
            actual_id_configs = accounting.get_apps_for_user(user)

            # should be ( (Application, ApplicationPolicy),
            #             (Application, ApplicationPolicy) ... )
            actual_configs = tuple((app, policy)
                                   for _, app, policy in actual_id_configs)

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
