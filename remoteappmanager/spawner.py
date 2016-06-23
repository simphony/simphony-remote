import os
from traitlets import Any, Unicode, default

from jupyterhub.spawner import LocalProcessSpawner
from jupyterhub import orm


class Spawner(LocalProcessSpawner):
    #: The instance of the orm Proxy.
    #: We use Any in agreement with base class practice.
    proxy = Any()

    #: The path of the configuration file for the cmd executable
    config_file_path = Unicode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # We get the first one. Strangely enough, jupyterhub has a table
        # containing potentially multiple proxies, but it's enforced to
        # contain only one.
        self.proxy = self.db.query(orm.Proxy).first()
        self.cmd = ['remoteappmanager']

    def get_args(self):
        args = super().get_args()
        args.append("--proxy-api-url={}".format(self.proxy.api_server.url))
        args.append("--config-file={}".format(self.config_file_path))
        return args

    def get_env(self):
        env = super().get_env()
        env["PROXY_API_TOKEN"] = self.proxy.auth_token
        return env

    @default("config_file_path")
    def _config_file_path_default(self):
        """Defines the default position of the configuration file for
        our utility. By default, it's the cwd of where we started up."""
        return os.path.join(os.getcwd(),
                            os.path.basename(self.cmd[0])+'_config.py')
