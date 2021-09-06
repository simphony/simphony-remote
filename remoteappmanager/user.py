from traitlets import HasTraits, Unicode, Any, List


class User(HasTraits):
    """Represents the user. It holds a reference to the ORM user, if
    available."""

    # The username as passed at the config line
    name = Unicode()

    #: Can be none if the username cannot be found in the database.
    account = Any()

    #: Reference to the authenticator method used for user login
    login_service = Unicode()

    #: Provide names of any default applications granted to the user
    #: This can be set in the JupyterHub configuration file
    demo_applications = List().tag(config=True)
