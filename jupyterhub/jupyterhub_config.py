# Configuration file for jupyterhub.
from jupyter_client.localinterfaces import public_ips

c = get_config()  # noqa

c.JupyterHub.ssl_key = 'test.key'
c.JupyterHub.ssl_cert = 'test.crt'

c.JupyterHub.hub_ip = public_ips()[0]

# Choose between system-user mode and virtual-user mode
setting_mode = ('system_user', 'virtual_user')[1]

if setting_mode == 'virtual_user':
    c.JupyterHub.spawner_class = ('remoteappmanager.jupyterhub.spawners.' +
                                  'VirtualUserSpawner')

    # Parent directory in which temporary directory is created for
    # each virtual user
    # Set this to a drive with well defined capacity quota
    # If unset, no workspace would be available
    c.Spawner.workspace_dir = '/tmp/remoteapp'

    # Uncomment this if you want to enable the use of the configuration
    # file for the spawned service, instead of using the defaults.
    # c.Spawner.config_file_path = 'remoteappmanager_config.py'

    # FIXME: replace me with other authenticator (e.g. GitHub OAuth...)
    c.JupyterHub.authenticator_class = (
        'remoteappmanager.jupyterhub.auth.WorldAuthenticator')

elif setting_mode == 'system_user':
    c.JupyterHub.spawner_class = ('remoteappmanager.jupyterhub.spawners.' +
                                  'SystemUserSpawner')
