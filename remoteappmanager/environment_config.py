import os
from traitlets import HasTraits, Unicode


class EnvironmentConfig(HasTraits):
    """Configuration options for the application server,
    originating from environment variables."""

    jpy_api_token = Unicode(help="The jupyterhub API token")

    proxy_api_token = Unicode(help="The Reverse Proxy API token")

    # Home is not part of it because we change it along the way,
    # so we can't rely on the value at startup.

    def parse_config(self):
        """Parses the command line arguments, and assign their
        values to our local traits.
        """

        for traitlet_name in self.traits().keys():
            envname = traitlet_name.upper()
            setattr(self, traitlet_name,
                    os.environ.get(envname, ""))
