from abc import ABCMeta, abstractmethod

from traitlets import HasTraits, Unicode, Bool


class ApplicationConfig(HasTraits):

    #: An ID for this configuration
    mapping_id = Unicode()

    #: Name of the docker image
    image = Unicode()

    #: Whether user's home directory is mounted
    allow_home = Bool(False)

    #: Source path (on the host machine) for the application specific data
    #: volume
    volume_source = Unicode(allow_none=True)

    #: Target path (on the container) for the application specific data
    #: volume
    volume_target = Unicode(allow_none=True)

    #: Read-write access mode for the application specific data volume
    #: (For docker, it is either "rw": read-write or "ro": read-only
    volume_mode = Unicode(allow_none=True)

    # Unhashable
    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, ApplicationConfig):
            return False

        for trait_name in self.trait_names():
            if getattr(self, trait_name) != getattr(other, trait_name):
                return False

        return True

    def __repr__(self):
        return "<{cls}({attrs})>".format(
            cls=self.__class__.__name__,
            attrs=", ".join("{0}={1!r}".format(
                trait_name, getattr(self, trait_name))
                            for trait_name in self.trait_names()
                        )
        )


class ABCDatabase(metaclass=ABCMeta):

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
        iterable : ApplicationConfig
        """
