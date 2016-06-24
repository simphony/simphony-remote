from traitlets import HasTraits, Unicode, Instance

from remoteappmanager.db import orm


class User(HasTraits):
    """Represents the user. It holds a reference to the ORM user, if
    available."""

    # The username as passed at the config line
    name = Unicode()

    #: Can be none if the username cannot be found in the database.
    orm_user = Instance(orm.User, allow_none=True)


