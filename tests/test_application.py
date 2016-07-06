import os

from tests.temp_mixin import TempMixin
from tornado import testing

from remoteappmanager.application import Application
from tests import utils


class TestApplication(TempMixin, testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)

        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

        self.command_line_config = utils.basic_command_line_config()
        self.file_config = utils.basic_file_config()
        self.file_config.db_url = "sqlite:///"+self.sqlite_file_path

        self.app = Application(self.command_line_config, self.file_config)

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

        super().tearDown()

    def test_initialization(self):
        app = self.app
        self.assertIsNotNone(app.command_line_config)
        self.assertIsNotNone(app.file_config)

        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)
        self.assertIsNotNone(app.reverse_proxy)
        self.assertIsNotNone(app.container_manager)
        self.assertIsNotNone(app.hub)
