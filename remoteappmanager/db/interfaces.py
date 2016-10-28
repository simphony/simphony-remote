from abc import ABCMeta, abstractmethod
import inspect as _inspect


class ABCApplication(metaclass=ABCMeta):
    """ Description of an application """

    def __init__(self, id, image):
        #: Numerical id
        self.id = id

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
    def get_user(self, *, user_name=None, id=None):
        """ Return a User for a given user_name or id, or return
        None if the User is not found. Only one argument is allowed.

        Parameters
        ----------
        user_name : str
            The user name

        id: int
            An id

        Returns
        -------
        user : opaque-type
           an user object that the database understands
        """

    @abstractmethod
    def get_apps_for_user(self, user):
        """ Return an iterable of ApplicationConfig for a given user

        Parameters
        ----------
        user : opaque-type
           Same type as the result of `get_user`

        Returns
        -------
        tuple
           each item of the tuple should be a tuple of
           (id, ABCApplication, ABCApplicationPolicy) where id is a string
           used for identifying (ABCApplication, ABCApplicationPolicy)
        """

    @abstractmethod
    def create_user(self, user_name):
        """Creates a user with the specified username, if the backend
        allows it.

        Parameters
        ----------
        user_name: str
            The user name

        Returns
        -------
        id: int
            The unique id of the user

        Raises
        ------
        exceptions.Exists
            If the user with that name already exists.
        """

    @abstractmethod
    def remove_user(self, *, user_name=None, id=None):
        """Removes a user by name or id, if the backend allows it.
        Only one argument is allowed. If the user is not present,
        does nothing.

        Parameters
        ----------
        user_name: str
            The user name
        """

    @abstractmethod
    def list_users(self):
        """Returns a list of all available users.

        Returns
        -------
        users: list
            A list of users.
        """

    @abstractmethod
    def create_application(self, app_name):
        """Creates a new application with the specified name.
        Raises if an application with the same name already exists

        Parameters
        ----------
        app_name: str
            The name of the application

        Returns
        -------
        id: int
            The id of the created application

        Raises
        ------
        exceptions.Exists
            If the application already exists.
        """

    @abstractmethod
    def remove_application(self, *, app_name=None, id=None):
        """Remove an existing application by name or id, depending
        what is provided. Only one argument is allowed.
        If the application is not present, does nothing.

        Parameters
        ----------
        app_name: str
            The name of the application

        id: int
            The id of the application

        Raises
        ------
        exception.NotFound
            If the application is not found.
        """

    @abstractmethod
    def list_applications(self):
        """List all available applications

        Returns
        -------
        applications: list
            A list of the available apps.
        """

    @abstractmethod
    def grant_access(self, app_name, user_name,
                     allow_home, allow_view, volume):
        """Grant access for user to application.

        Parameters
        ----------
        app_name: str
            The name of the application

        user_name: str
            The name of the user

        allow_home: bool
            If the home workspace should be mounted.

        allow_view: bool
            If the session should be visible by others.

        volume: str
            A volume to mount in the format source_path:target_path:mode
            mode being "ro" or "rw".
            (e.g. "/host/path:/container/path:ro").

        Raises
        ------
        exception.NotFound:
            if the app or user are not found.
        ValueError:
            if the volume string is invalid.

        Returns
        -------
        id : str
            A 32 characters id (mapping_id)
        """

    @abstractmethod
    def revoke_access(self, app_name, user_name,
                      allow_home, allow_view, volume):
        """Revoke access for user to application.

        Parameters
        ----------
        app_name: str
            The name of the application

        user_name: str
            The name of the user

        allow_home: bool
            If the home workspace should be mounted.

        allow_view: bool
            If the session should be visible by others.

        volume: str
            A volume to mount in the format source_path:target_path:mode
            mode being "ro" or "rw".
            (e.g. "/host/path:/container/path:ro").

        Raises
        ------
        exception.NotFound:
            if the app or user are not found.
        ValueError:
            if the volume string is invalid.
        """

    @abstractmethod
    def revoke_access_by_id(self, mapping_id):
        """Like revoke_access, but uses the mapping id instead."""
