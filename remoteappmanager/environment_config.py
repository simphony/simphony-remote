import os
from traitlets import HasTraits, Unicode


class EnvironmentConfig(HasTraits):
    """Configuration options for the application server,
    originating from environment variables."""

    #: Token for JupyterHub API. Originates from JUPYTERHUB_API_TOKEN
    jpy_api_token = Unicode(help="The JupyterHub API token")

    #: Token for the ReverseProxy API. Originates from
    #: PROXY_API_TOKEN
    proxy_api_token = Unicode(help="The Reverse Proxy API token")

    # This is the host of the hub. It's always empty (jupyterhub decision).
    # Originates from JUPYTERHUB_HOST
    hub_host = Unicode(help="The url of the jupyterhub server")

    # This is a url path that sends the request to jupyterhub.
    # It's normally /hub/. Originates from JUPYTERHUB_SERVICE_PREFIX
    hub_prefix = Unicode(help="The url prefix of the jupyterhub")

    # This is a full url to reach the hub api (e.g. for authentication check)
    # Originates from JUPYTERHUB_API_URL
    hub_api_url = Unicode(help="The url of the jupyterhub REST API")

    # Home is not part of it because we change it along the way,
    # so we can't rely on the value at startup.

    def parse_config(self):
        """Parses the environment variables, and assign their
        values to our local traits.
        """
        mapping = {
            "JUPYTERHUB_API_TOKEN": 'jpy_api_token',
            "PROXY_API_TOKEN": 'proxy_api_token',
            "JUPYTERHUB_HOST": 'hub_host',
            "JUPYTERHUB_SERVICE_PREFIX": 'hub_prefix',
            "JUPYTERHUB_API_URL": 'hub_api_url'
        }
        for envname, traitlet_name in mapping.items():
            setattr(self, traitlet_name,
                    os.environ.get(envname, ""))
