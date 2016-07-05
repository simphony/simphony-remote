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

        #: Mode for read-write access (ro: Read-only, rw: Read-write)
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
        """ Return a User for a given user_name, or None
        if the user name is not found.

        Parameters
        ----------
        user_name : str

        Returns
        -------
        user : User
            a User object that the Database understands
        """

    @abstractmethod
    def get_apps_for_user(self, user_name):
        """ Return an iterable of ApplicationConfig for a given user name

        Parameters
        ----------
        user_name: str

        Returns
        -------
        application_spec: tuple
           each item of the tuple should be a tuple of
           (id, ABCApplication, ABCApplicationPolicy) where id is a string
           used for identifying (ABCApplication, ABCApplicationPolicy)
        """
