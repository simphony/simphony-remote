import os

from tests.temp_mixin import TempMixin
from tornado import testing

from remoteappmanager.application import Application

from tests import utils
from tests.db import test_csv_db


class TestApplication(TempMixin, testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)

        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        # File config with orm.AppAccounting
        self.file_config = utils.basic_file_config()
        self.command_line_config = utils.basic_command_line_config()

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

        super().tearDown()

    def test_initialization_with_sqlite_db(self):
        # Initialise database
        sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(sqlite_file_path)

        self.file_config.accounting_class = (
            "remoteappmanager.db.orm.AppAccounting")
        self.file_config.accounting_kwargs = {
            "url": "sqlite:///"+sqlite_file_path}

        app = Application(self.command_line_config, self.file_config)

        self.assertIsNotNone(app.command_line_config)
        self.assertIsNotNone(app.file_config)

        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)
        self.assertIsNotNone(app.reverse_proxy)
        self.assertIsNotNone(app.container_manager)
        self.assertIsNotNone(app.hub)
        self.assertEqual(app.user.name, "username")
        self.assertEqual(app.user.orm_user, None)

    def test_error_default_value_with_unimportable_accounting(self):
        self.file_config.accounting_class = "not.importable.Class"
        app = Application(self.command_line_config, self.file_config)

        with self.assertRaises(ImportError):
            app.db


# FIXME: Some of these tests are the same and should be refactored
# Not doing it now to prevent more merge conflict with PR #52
class TestApplicationWithCSV(TempMixin, testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)

        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        self.command_line_config = utils.basic_command_line_config()
        self.file_config = utils.basic_file_config()

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

        super().tearDown()

    def test_initialization(self):
        self.file_config.accounting_class = (
            "remoteappmanager.db.csv_db.CSVAccounting")

        csv_file = os.path.join(self.tempdir, 'testing.csv')
        self.file_config.accounting_kwargs = {"csv_file_path": csv_file}

        test_csv_db.write_csv_file(csv_file,
                                   test_csv_db.GoodTable.headers,
                                   test_csv_db.GoodTable.records)

        app = Application(self.command_line_config, self.file_config)

        self.assertIsNotNone(app.command_line_config)
        self.assertIsNotNone(app.file_config)
        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)
        self.assertEqual(app.user.name, "username")
        self.assertIsInstance(app.user.orm_user, test_csv_db.CSVUser)
