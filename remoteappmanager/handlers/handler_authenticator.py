from tornado import gen


class Authenticator:
    """Base authenticator class for the web handlers"""
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        """Called by the handler to authenticate the user.
        The handler passes itself as an argument, and expects a valid
        handler.current_user value, or None"""
        return None


class HubAuthenticator(Authenticator):
    """Authenticator that uses the remote JupyterHub to validate
    the request.

    Deprecated as of remoteappmanager 2.2.0
    """
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        # Authenticate the user against the hub. We can't use get_current_user
        # because we want to do it asynchronously.
        webapp = handler.application
        hub = webapp.hub
        cookie_name = handler.settings["cookie_name"]
        user_cookie = handler.get_cookie(cookie_name)
        user = None

        if user_cookie:
            user_data = (yield hub.verify_token(cookie_name, user_cookie))
            if user_data.get('name', '') == webapp.user.name:
                user = webapp.user

        return user


class HubOAuthenticator(Authenticator):
    """Authenticator that uses the remote JupyterHub as an OAuth
    provider to validate the request."""
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        # Authenticate the user against the hub. Expects the handler
        # to inherit from the jupyterhub.services.auth.HubOAuthenticated
        # mixin
        webapp = handler.application
        hub = webapp.hub
        user = None

        user_data = yield hub.get_user(handler)
        if user_data.get('name', '') == webapp.user.name:
            user = webapp.user

        return user
