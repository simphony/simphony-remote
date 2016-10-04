from traitlets import HasTraits, Unicode, Any


class User(HasTraits):
    """Represents the user. It holds a reference to the ORM user, if
    available."""

    # The username as passed at the config line
    name = Unicode()

    #: Can be None if the username cannot be found in the database.
    account = Any()

    def is_admin(self):
        """Returns True if the user is recognized and is also an admin
        as indicated by the underlying accounting mechanism"""
        return self.account and self.account.is_admin()
