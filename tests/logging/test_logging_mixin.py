import unittest
from unittest import mock

from remoteappmanager.logging.logging_mixin import LoggingMixin


class Logged(LoggingMixin):
    pass


class TestLoggingMixin(unittest.TestCase):
    def test_issue(self):
        l = Logged()
        with mock.patch("tornado.log.app_log.error") as mock_error:
            ref = l.log.issue("hello")
            self.assertIn("hello. Ref: "+str(ref), mock_error.call_args[0][0])
            ref = l.log.issue("hello", Exception("Boom!"))
            self.assertIn("hello : Boom!. Ref: "+str(ref),
                          mock_error.call_args[0][0])
