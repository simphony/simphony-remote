from abc import abstractmethod, ABCMeta
from collections import Iterable

# FIXME: remove these imports when the dummy test case at the bottom
# of this file is removed
import unittest
from collections import namedtuple
from remoteappmanager.db.interfaces import ABCDatabase, ApplicationConfig


class ABCTestDatabase(metaclass=ABCMeta):

    def setUp(self, usernames, application_configs):
        """ Given a list of usernames, associate a list of
        ApplicationConfig for each user.

        Examples
        --------
        setUp(('user1', 'user2'),
              ( # user1
                (ApplicationConfig(...),
                 ApplicationConfig(...)),
                # user2
                (ApplicationConfig(...),) )
        """
        if not (usernames and application_configs):
            raise ValueError("usernames and application_configs must not "
                             "be empty")

        for configs in application_configs:
            if not isinstance(configs, Iterable):
                raise TypeError("{!0} is not iterable.".format(configs))

        self.user_config_mappings = dict(zip(usernames, application_configs))

    @abstractmethod
    def create_database(self):
        """ Create a database that complies with ABCDatabase """

    @abstractmethod
    def test_get_user_by_name(self):
        """ Test ABCDatabase.get_user_by_name """

    def test_get_apps_for_user(self):
        """ Test get_appgs_for_user returns an iterable of ApplicationConfig
        """
        database = self.create_database()

        for username, expected_configs in self.user_config_mappings.items():
            actual_configs = database.get_apps_for_user(username)
            self.assertSetEqual(set(actual_configs), set(expected_configs))


# -------------------------------------------------------------------------
# FIXME: The following is a dummy test case
# Remove the following when the ABCDatabase is used and tested by actual
# database
# -------------------------------------------------------------------------
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
