import os
from jupyter_client.localinterfaces import public_ips

c = get_config()  # noqa

# c.JupyterHub.ssl_key = 'test.key'
# c.JupyterHub.ssl_cert = 'test.crt'

c.JupyterHub.port = 9090
c.JupyterHub.proxy_api_port = 9091
c.JupyterHub.hub_ip = public_ips()[0]
c.JupyterHub.hub_port = 9092
c.JupyterHub.base_url = 'simphony-remote'

c.JupyterHub.spawner_class = (
    'remoteappmanager.jupyterhub.spawners.VirtualUserSpawner'
)

# Parent directory in which temporary directory is created for
# each virtual user
# Set this to a drive with well defined capacity quota
# If unset, no workspace would be available
c.Spawner.workspace_dir = '/tmp/remoteapp'

c.JupyterHub.authenticator_class = (
    'remoteappmanager.jupyterhub.auth.GitHubWhitelistAuthenticator')
c.Authenticator.admin_users = {"simphony-admin"}

# You have to setup github appropriately for this to work.
# Once done, you will get the client id and secret.
c.GitHubWhitelistAuthenticator.oauth_callback_url = (
    "https://example.com/oauth_callback")
c.GitHubWhitelistAuthenticator.client_id = ""
c.GitHubWhitelistAuthenticator.client_secret = ""

# Whitelist file contains the usernames that are allowed in.
# GitHub authenticates anybody with a github account, but to
# restrict who can get in, you have to specify their accounts
# in the whitelist file. An empty or unexistent file means everybody
# is allowed in
c.GitHubWhitelistAuthenticator.whitelist_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "whitelist.txt")
