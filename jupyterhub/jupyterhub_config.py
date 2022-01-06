# Configuration file for jupyterhub.
import os
from jupyter_client.localinterfaces import public_ips
from jupyterhub.utils import new_token

c = get_config()  # noqa

c.JupyterHub.ssl_key = 'test.key'
c.JupyterHub.ssl_cert = 'test.crt'

c.JupyterHub.hub_ip = public_ips()[0] if len(public_ips()) else '127.0.0.1'

c.ConfigurableHTTPProxy.command = [
    'configurable-http-proxy',
    f'--default-target=http://{c.JupyterHub.hub_ip}:8081']
c.ConfigurableHTTPProxy.api_url = "http://127.0.0.1:8001"
c.ConfigurableHTTPProxy.auth_token = new_token()

c.JupyterHub.logo_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'remoteappmanager/static/images/header_logo.png'
)

# Choose between system-user mode and virtual-user mode
setting_mode = ('system_user', 'virtual_user', 'dummy_user')[1]

if setting_mode == 'virtual_user':
    c.JupyterHub.spawner_class = ('remoteappmanager.jupyterhub.spawners.'
                                  'VirtualUserSpawner')

    # Parent directory in which temporary directory is created for
    # each virtual user
    # Set this to a drive with well defined capacity quota
    # If unset, no workspace would be available
    c.Spawner.workspace_dir = '/tmp/remoteapp'

    # Uncomment this if you want to enable the use of the configuration
    # file for the spawned service, instead of using the defaults.
    # c.Spawner.config_file_path = 'remoteappmanager_config.py'

    # As of jupyterhub>0.8.0, there's no convenient way to obtain a
    # reference between the Spawner and ConfigurableHTTProxy objects
    # during runtime, so we simply assign common traits once and do
    # not expect them to change
    c.Spawner.proxy_api_url = c.ConfigurableHTTPProxy.api_url
    c.Spawner.proxy_auth_token = c.ConfigurableHTTPProxy.auth_token

    # FIXME: replace me with other authenticator (e.g. GitHub OAuth...)
    c.JupyterHub.authenticator_class = (
        'remoteappmanager.jupyterhub.auth.WorldAuthenticator')
    c.Authenticator.admin_users = {"admin"}

elif setting_mode == 'system_user':
    c.JupyterHub.spawner_class = ('remoteappmanager.jupyterhub.spawners.'
                                  'SystemUserSpawner')
    c.Authenticator.admin_users = {os.environ["USER"]}

elif setting_mode == 'dummy_user':
    # Make sure to run: `pip install dev-requirements.txt` first
    c.JupyterHub.spawner_class = (
        'simplespawner.SimpleLocalProcessSpawner')
    c.JupyterHub.authenticator_class = (
        'remoteappmanager.jupyterhub.auth.WorldAuthenticator')
