# Configuration file for jupyterhub.
from jupyter_client.localinterfaces import public_ips

c = get_config()  # noqa

c.JupyterHub.ssl_key = 'test.key'
c.JupyterHub.ssl_cert = 'test.crt'
c.JupyterHub.spawner_class = 'remoteappmanager.spawner.Spawner'

c.JupyterHub.hub_ip = public_ips()[0]
