from tornado import gen

from jupyterhub.handlers import LogoutHandler as _LogoutHandler
from jupyterhub.handlers import LoginHandler


class LogoutHandler(_LogoutHandler):
    """ Custom logout handler that also closes servers of admin
    users, so that spawner options form will be shown during every login
    """
    @gen.coroutine
    def get(self):
        user = self.get_current_user()
        if user:
            # Ensures admin sessions are shut down when user
            # logs out so that the spawner options form is
            # shown upon subsequent logins
            # TODO: replace for configuring shutdown_on_logout option
            #  once running on jupyterhub>=1.0.0
            if user.admin and user.spawner is not None:
                self.log.info(f"Shutting down {user.name}'s server")
                yield gen.maybe_future(self.stop_single_user(user))
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()
            self.statsd.incr('logout')
        self.redirect(self.settings['login_url'], permanent=False)


class SimphonyRemoteAuthMixin:

    def get_handlers(self, app):
        """Includes standard LoginHandler and modified LogoutHandler that
        closes admin sessions upon signing out
        """
        return [
            ('/login', LoginHandler),
            ('/logout', LogoutHandler)
        ]
