from unittest import mock, TestCase

from remoteappmanager.logging.logging_mixin import LoggingMixin


class Logged(LoggingMixin):
    pass


class TestLoggingMixin(TestCase):
    def test_issue(self):
        logged = Logged()
        with mock.patch("tornado.log.app_log.error") as mock_error:
            ref = logged.log.issue("hello")
            self.assertIn(
                "hello. Ref: "+str(ref), mock_error.call_args[0][0])
            ref = logged.log.issue("hello", Exception("Boom!"))
            self.assertIn("hello : Boom!. Ref: "+str(ref),
                          mock_error.call_args[0][0])
