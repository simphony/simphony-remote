# Configuration file for jupyterhub.
import os
from jupyter_client.localinterfaces import public_ips

c = get_config()  # noqa

c.JupyterHub.ssl_key = 'test.key'
c.JupyterHub.ssl_cert = 'test.crt'

c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.spawner_class = (
    'remoteappmanager.jupyterhub.spawners.VirtualUserSpawner'
    )

# Parent directory in which temporary directory is created for
# each virtual user
# Set this to a drive with well defined capacity quota
# If unset, no workspace would be available
c.Spawner.workspace_dir = '/tmp/remoteapp'

# Uncomment this if you want to enable the use of the configuration
# file for the spawned service, instead of using the defaults.
# c.Spawner.config_file_path = 'remoteappmanager_config.py'

c.JupyterHub.authenticator_class = (
    'remoteappmanager.jupyterhub.auth.WorldAuthenticator')
c.Authenticator.admin_users = {"admin"}
