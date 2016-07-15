import unittest
from unittest import mock

from click.testing import CliRunner

from remoteappmanager.cli.remoteapprest import __main__ as remoteapprest


class TestRemoteAppREST(unittest.TestCase):
    def _remoteapprest(self, argstring):
        runner = CliRunner()
        result = runner.invoke(remoteapprest.cli,
                               argstring.split(),
                               catch_exceptions=False)

        return result.exit_code, result.output

    def test_login_command(self):
        with mock.patch('requests.post') as mock_post, \
             mock.patch('requests.utils.'
                        'dict_from_cookiejar') as mock_dict_from:

            mock_post.return_value = mock.Mock()
            mock_post.return_value.status_code = 302
            mock_post.cookies = []
            mock_dict_from.return_value = {}
            self._remoteapprest("login "
                                "--username=user "
                                "--password=password "
                                "http://example.com/")
            self.assertEqual(mock_post.call_args[0][0],
                             'http://example.com/hub/login')

            self.assertEqual(mock_post.call_args[0][1],
                             dict(username="user",
                                  password="password"))
