from abc import ABCMeta, abstractmethod
import inspect as _inspect


class ABCApplication(metaclass=ABCMeta):
    """ Description of an application """

    def __init__(self, image):

        #: Name of the image
        self.image = image

    def __repr__(self):
        args = _inspect.getargs(ABCApplication.__init__.__code__).args[1:]

        return "<{cls}({spec})>".format(
            cls=self.__class__.__name__,
            spec=", ".join("{0}={1!r}".format(arg, getattr(self, arg))
                           for arg in args))


class ABCApplicationPolicy(metaclass=ABCMeta):
    """ Policy for an application
    """

    def __init__(self, allow_home=False, allow_view=False, allow_common=False,
                 volume_source=None, volume_target=None, volume_mode=None):

        #: Is the home directory mounted
        self.allow_home = allow_home

        #: Is the application viewable by others
        self.allow_view = allow_view

        #: Is the common data volume for the application mounted
        self.allow_common = allow_common

        #: Source path for the common data volume on the host machine
        self.volume_source = volume_source

        #: Target mount point of the common data volume in the application
        self.volume_target = volume_target

        #: Mode for read-write access (ro = Read-only. rw = Read-write)
        self.volume_mode = volume_mode

    def __repr__(self):
        args = _inspect.getargs(
            ABCApplicationPolicy.__init__.__code__).args[1:]

        return "<{cls}({spec})>".format(
            cls=self.__class__.__name__,
            spec=", ".join("{0}={1!r}".format(arg, getattr(self, arg))
                           for arg in args))


class ABCAccounting(metaclass=ABCMeta):
    """ Main accounting interface required by the single user application.
    """

    @abstractmethod
    def get_user_by_name(self, user_name):
        """ Return a User for a given user_name, or return
        None if the User name is not found.

        Parameters
        ----------
        user_name : str

        Returns
        -------
        account : opaque-type
           an object that the database understands
        """

    @abstractmethod
    def get_apps_for_user(self, account):
        """ Return an iterable of ApplicationConfig for a given account

        Parameters
        ----------
        account : opaque-type
           Same type as the result of `get_user_by_name`

        Returns
        -------
        tuple
           each item of the tuple should be a tuple of
           (id, ABCApplication, ABCApplicationPolicy) where id is a string
           used for identifying (ABCApplication, ABCApplicationPolicy)
        """

    @abstractmethod
    def create_user(self, user_name):
        """Creates a new user, if the backend allows it.
        """

    @abstractmethod
    def remove_user(self, user_name):
        """Removes a user, if the backend allows it.
        """

    @abstractmethod
    def list_users(self):
        """Returns a list of all available users.
        """

    @abstractmethod
    def create_application(self, app_name):
        """Create a new application.
         if the backend allows it."""

    @abstractmethod
    def remove_application(self, app_name):
        """Remove an existing application"""

    @abstractmethod
    def list_applications(self):
        """List all available applications."""

    @abstractmethod
    def grant_access(self, app_name, user_name,
                     allow_home, allow_view, volume):
        """Grant access for user to application."""

    @abstractmethod
    def revoke_access(self, app_name, user_name,
                      allow_home, allow_view, volume):
        """Revoke access for user to application"""
