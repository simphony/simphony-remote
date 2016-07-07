from traitlets import HasTraits, Unicode, Any


class User(HasTraits):
    """Represents the user. It holds a reference to the ORM user, if
    available."""

    # The username as passed at the config line
    name = Unicode()

    # FIXME: orm_user is Any to support other database implementation

    #: Can be none if the username cannot be found in the database.
    orm_user = Any()
