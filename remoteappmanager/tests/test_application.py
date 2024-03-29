import os
from unittest import mock
from unittest.mock import patch

from tornado import testing
from traitlets.traitlets import TraitError

from remoteappmanager.application import Application
from remoteappmanager.db.tests import test_csv_db
from remoteappmanager.tests import utils
from remoteappmanager.tests.temp_mixin import TempMixin


class DummyDB:
    def __init__(self, *args, **kwargs):
        pass


class TestApplication(TempMixin,
                      testing.AsyncTestCase,
                      testing.ExpectLog):
    def setUp(self):
        super().setUp()

        # File config with orm.ORMDatabase
        self.file_config = utils.basic_file_config()
        self.command_line_config = utils.basic_command_line_config()
        self.environment_config = utils.basic_environment_config()

    def test_initialization_with_sqlite_db(self):
        # Initialise database
        sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(sqlite_file_path)

        self.file_config.database_class = (
            "remoteappmanager.db.orm.ORMDatabase")
        self.file_config.database_kwargs = {
            "url": "sqlite:///"+sqlite_file_path}

        app = Application(self.command_line_config,
                          self.file_config,
                          self.environment_config)

        self.assertIsNotNone(app.command_line_config)
        self.assertIsNotNone(app.file_config)
        self.assertIsNotNone(app.environment_config)

        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)
        self.assertIsNotNone(app.reverse_proxy)
        self.assertIsNotNone(app.container_manager)
        self.assertIsNotNone(app.hub)
        self.assertEqual(app.user.name, "johndoe")
        self.assertEqual(app.user.login_service, "")
        self.assertIsNone(app.user.account)

    def test_error_default_value_with_unimportable_accounting(self):
        self.file_config.database_class = "not.importable.Class"
        app = Application(self.command_line_config,
                          self.file_config,
                          self.environment_config)

        with self.assertRaises(ImportError):
            app.db

    def test_db_default_value_with_accounting_wrong_subclass(self):
        self.file_config.database_class = (
            "remoteappmanager.tests.test_application.DummyDB")
        app = Application(self.command_line_config,
                          self.file_config,
                          self.environment_config)

        with self.assertRaises(TraitError):
            app.db

    def test_initialization(self):
        self.file_config.database_class = (
            "remoteappmanager.db.csv_db.CSVDatabase")

        csv_file = os.path.join(self.tempdir, 'testing.csv')
        self.file_config.database_kwargs = {"csv_file_path": csv_file}

        test_csv_db.write_csv_file(csv_file,
                                   test_csv_db.GoodTable.headers,
                                   test_csv_db.GoodTable.records)

        app = Application(self.command_line_config,
                          self.file_config,
                          self.environment_config)

        self.assertIsNotNone(app.command_line_config)
        self.assertIsNotNone(app.file_config)
        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)
        self.assertEqual(app.user.name, "johndoe")
        self.assertIsInstance(app.user.account, test_csv_db.CSVUser)

    def test_initialization_with_demo_applications(self):
        # Initialise database
        sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(sqlite_file_path)

        # Add demo app to database using remoteappmanager API
        from remoteappmanager.db.orm import ORMDatabase
        test_db = ORMDatabase("sqlite:///"+sqlite_file_path)
        test_db.create_application('my-demo-app')
        del test_db

        self.file_config.database_class = (
            "remoteappmanager.db.orm.ORMDatabase")
        self.file_config.database_kwargs = {
            "url": "sqlite:///"+sqlite_file_path}
        self.file_config.demo_applications = {
            'my-demo-app': {'allow_home': True}
        }
        self.file_config.auto_user_creation = True

        app = Application(self.command_line_config,
                          self.file_config,
                          self.environment_config)

        self.assertEqual(app.user.name, "johndoe")
        self.assertIsNotNone(app.user.account)

        user_apps = app.db.get_accounting_for_user(app.user.account)
        app_account = user_apps[0]
        self.assertEqual(app_account.application.image, 'my-demo-app')
        self.assertIsNone(
            app_account.application_policy.app_license)
        self.assertTrue(
            app_account.application_policy.allow_home)
        self.assertTrue(
            app_account.application_policy.allow_view)
        self.assertIsNone(
            app_account.application_policy.volume_source)
        self.assertIsNone(
            app_account.application_policy.volume_target)
        self.assertFalse(
            app_account.application_policy.allow_startup_data)

    def test_start(self):
        with patch(
                "remoteappmanager.application.Application.listen"
        ) as listen, \
             patch("tornado.ioloop.IOLoop.current") as current:

            current_io = mock.Mock()
            current.return_value = current_io

            app = Application(self.command_line_config,
                              self.file_config,
                              self.environment_config)

            app.start()

            self.assertTrue(listen.called)
            self.assertTrue(current_io.start.called)
