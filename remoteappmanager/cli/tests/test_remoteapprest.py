import os
import json
import unittest
from unittest import mock

from click.testing import CliRunner

from remoteappmanager.cli.remoteapprest import __main__ as remoteapprest
from remoteappmanager.cli.remoteapprest.__main__ import Credentials
from remoteappmanager.tests.temp_mixin import TempMixin


class TestRemoteAppREST(TempMixin, unittest.TestCase):
    def _remoteapprest(self, argstring):
        runner = CliRunner()
        result = runner.invoke(remoteapprest.cli,
                               argstring.split(),
                               catch_exceptions=False)

        return result.exit_code, result.output

    def test_credentials_class(self):
        credentials_file = os.path.join(self.tempdir,
                                        "credentials")
        with open(credentials_file, "w") as f:
            f.write("url\n")
            f.write("username\n")
            f.write("cookie1=foo\n")
            f.write("cookie2=bar\n")

        credentials = Credentials.from_file(credentials_file)
        self.assertEqual(credentials.url, "url")
        self.assertEqual(credentials.username, "username")
        self.assertEqual(credentials.cookies, {"cookie1": "foo",
                                               "cookie2": "bar"})

    def test_login(self):
        with mock.patch('requests.post') as mock_post, \
             mock.patch('requests.utils.'
                        'dict_from_cookiejar') as mock_dict_from:

            mock_post.return_value = mock.Mock()
            mock_post.return_value.status_code = 302
            mock_post.cookies = []
            mock_dict_from.return_value = {}
            credentials_file = os.path.join(self.tempdir, "credentials")
            self._remoteapprest(
                                "--credentials-file={} "
                                "login "
                                "--username=user "
                                "--password=password "
                                "http://example.com/".format(
                                    credentials_file)
                                )
            self.assertEqual(mock_post.call_args[0][0],
                             'http://example.com/hub/login')

            self.assertEqual(mock_post.call_args[0][1],
                             dict(username="user",
                                  password="password"))
            self.assertTrue(os.path.exists(credentials_file))

    def test_app_available(self):
        with mock.patch('requests.get') as mock_get, \
            mock.patch("remoteappmanager.cli.remoteapprest.__main__."
                       "Credentials.from_file") as mock_from_file:

            responses = [
                mock.Mock(),
                mock.Mock(),
                mock.Mock()
            ]
            responses[0].content = json.dumps(
                {'items': ['1', '2']}
            ).encode("utf-8")

            responses[1].content = json.dumps(
                {'image': {"ui_name": "foo"}}
            ).encode("utf-8")

            responses[2].content = json.dumps(
                {'image': {"ui_name": "bar"}}
            ).encode("utf-8")

            mock_get.side_effect = responses

            mock_from_file.return_value = self.get_mock_credentials()

            self._remoteapprest("app available")
            self.assertEqual(mock_get.call_args_list[0][0][0],
                             "/user/bar/api/v1/applications/")
            self.assertEqual(mock_get.call_args_list[1][0][0],
                             "/user/bar/api/v1/applications/1/")
            self.assertEqual(mock_get.call_args_list[2][0][0],
                             "/user/bar/api/v1/applications/2/")

    def test_app_running(self):
        with mock.patch('requests.get') as mock_get, \
                mock.patch("remoteappmanager.cli.remoteapprest.__main__."
                           "Credentials.from_file") as mock_from_file:

            responses = [
                mock.Mock(),
                mock.Mock(),
                mock.Mock()
            ]
            responses[0].content = json.dumps(
                {'items': ['1', '2']}
            ).encode("utf-8")

            responses[1].content = json.dumps(
                {'image_name': "foo"}
            ).encode("utf-8")

            responses[2].content = json.dumps(
                {'image_name': "bar"}
            ).encode("utf-8")

            mock_get.side_effect = responses

            mock_from_file.return_value = self.get_mock_credentials()

            self._remoteapprest("app running")
            self.assertEqual(mock_get.call_args_list[0][0][0],
                             "/user/bar/api/v1/containers/")
            self.assertEqual(mock_get.call_args_list[1][0][0],
                             "/user/bar/api/v1/containers/1/")
            self.assertEqual(mock_get.call_args_list[2][0][0],
                             "/user/bar/api/v1/containers/2/")

    def test_app_start(self):
        with mock.patch('requests.post') as mock_post, \
                mock.patch("remoteappmanager.cli.remoteapprest.__main__."
                           "Credentials.from_file") as mock_from_file:

            mock_from_file.return_value = self.get_mock_credentials()

            self._remoteapprest("app start 1")
            self.assertEqual(mock_post.call_args[0][0],
                             "/user/bar/api/v1/containers/")
            self.assertEqual(mock_post.call_args[0][1],
                             json.dumps({"mapping_id": "1"}))

    def test_app_stop(self):
        with mock.patch('requests.delete') as mock_delete, \
                mock.patch("remoteappmanager.cli.remoteapprest.__main__."
                           "Credentials.from_file") as mock_from_file:

            mock_from_file.return_value = self.get_mock_credentials()

            self._remoteapprest("app stop 1")
            self.assertEqual(mock_delete.call_args[0][0],
                             "/user/bar/api/v1/containers/1/")

    def get_mock_credentials(self):
        credentials = mock.Mock()
        credentials.url = "foo"
        credentials.username = "bar"
        credentials.cookies = {}
        return credentials
