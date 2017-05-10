from abc import ABCMeta, abstractmethod
import inspect as _inspect


class ABCImage(metaclass=ABCMeta):
    """ Description of an image in the database"""

    def __init__(self, id, name):
        #: Numerical id
        self.id = id

        #: Name of the image
        self.name = name

    def __repr__(self):
        args = _inspect.getargs(ABCImage.__init__.__code__).args[1:]

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
    def __init__(self, id, user, application, application_policy):
        self.id = id
        self.user = user
        self.application = application
        self.application_policy = application_policy


class ABCDatabase(metaclass=ABCMeta):
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
    def get_accounting_for_user(self, user):
        """ Returns the accounting information for a given user

        Parameters
        ----------
        user : opaque-type
           Same type as the result of `get_user`

        Returns
        -------
        list
           each item of the list should be an instance satisfying the
           ABCAccounting format (duck typing)
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
    def create_image(self, name):
        """Creates a new image with the specified name.
        Raises if an image with the same name already exists

        Parameters
        ----------
        name: str
            The name of the image

        Returns
        -------
        id: int
            The id of the created image

        Raises
        ------
        exceptions.Exists
            If the image already exists.
        """

    @abstractmethod
    def remove_image(self, *, name=None, id=None):
        """Remove an existing image by name or id, depending
        what is provided. Only one argument is allowed.
        If the image is not present, does nothing.

        Parameters
        ----------
        name: str
            The name of the image

        id: int
            The id of the image
        """

    @abstractmethod
    def list_images(self):
        """List all available images

        Returns
        -------
        images: list
            A list of the available images
        """

    @abstractmethod
    def grant_access(self, image_name, user_name,
                     allow_home, allow_view, volume):
        """Grant access for user to image.

        Parameters
        ----------
        image_name: str
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
    def revoke_access(self, image_name, user_name,
                      allow_home, allow_view, volume):
        """Revoke access for user to image

        Parameters
        ----------
        image_name: str
            The name of the image

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
