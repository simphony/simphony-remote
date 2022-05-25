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
    """Authenticator that uses the remote JupyterHub as an Auth
    provider to validate the request."""
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        """Authenticate the handler application's user session
        against the hub.

        Parameters
        ----------
        handler : tornado.web.RequestHandler or
                  tornadowebapi.resource_handler.ResourceHandler
            Handler to authenticate against the JupyterHub

        Returns
        -------
        user : remoteappmanager.user.User or None
            Internal model representing authenticated user
        """
        # Authenticate the user against the hub.
        webapp = handler.application
        hub = webapp.hub
        user = None

        user_data = yield hub.get_user(handler)
        if user_data.get('name', '') == webapp.user.name:
            user = webapp.user

        return user
