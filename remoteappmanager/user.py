from traitlets import HasTraits, Unicode, Any


class User(HasTraits):
    """Represents the user. It holds a reference to the ORM user, if
    available."""

    # The username as passed at the config line
    name = Unicode()

    #: Can be none if the username cannot be found in the database.
    account = Any()

    #: Reference to the authenticator method used for user login
    login_service = Unicode()
