import os
import shutil
import tempfile

from traitlets import Any, Unicode, default
from tornado import gen

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


class VirtualUserSpawner(LocalProcessSpawner):
    #: The instance of the orm Proxy.
    #: We use Any in agreement with base class practice.
    proxy = Any()

    #: The path of the configuration file for the cmd executable
    config_file_path = Unicode(config=True)

    #: Directory in which temporary home directory for the virtual
    #: user is created.  No directory is created if this is not
    #: defined.
    workspace_dir = Unicode(config=True)

    #: The path to the temporary workspace directory
    _virtual_workspace = Unicode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # We get the first one. Strangely enough, jupyterhub has a table
        # containing potentially multiple proxies, but it's enforced to
        # contain only one.
        self.proxy = self.db.query(orm.Proxy).first()
        self.cmd = ['remoteappmanager']

    def make_preexec_fn(self, name):
        # We don't set user uid for virtual user
        # Nor do we try to start the process in the user's
        # home directory (it does not exist)
        pass

    def load_state(self, state):
        super().load_state(state)
        virtual_workspace = state.get('virtual_workspace')
        if virtual_workspace:
            if os.path.isdir(virtual_workspace):
                self._virtual_workspace = virtual_workspace
            else:
                self.log.warn('Previous virtual workspace is gone.')

    def get_state(self):
        state = super().get_state()
        if self._virtual_workspace:
            state['virtual_workspace'] = self._virtual_workspace
        return state

    def clear_state(self):
        super().clear_state()
        self._virtual_workspace = ''

    def get_args(self):
        args = super().get_args()
        args.append("--proxy-api-url={}".format(self.proxy.api_server.url))
        args.append("--config-file={}".format(self.config_file_path))
        return args

    def user_env(self, env):
        env['USER'] = self.user.name

        if self._virtual_workspace:
            env['HOME'] = self._virtual_workspace

        return env

    def get_env(self):
        # LocalProcessSpawner.get_env calls user_env as well
        env = super().get_env()
        env["PROXY_API_TOKEN"] = self.proxy.auth_token
        return env

    @gen.coroutine
    def start(self):
        """ Start the process and create the virtual user's
        temporary home directory if `workspace_dir` is set
        """
        # Create the temporary directory as the user's workspace
        if self.workspace_dir and not self._virtual_workspace:
            self._virtual_workspace = tempfile.mkdtemp(
                dir=self.workspace_dir)
            self.log.info("Created temporary directory: %s",
                          self._virtual_workspace)

        # Make sure we clean up in case `start` fails
        try:
            super().start()
        except Exception as exception:
            self._clean_up_workspace_dir()
            raise exception

    @gen.coroutine
    def stop(self, now=False):
        """ Stop the process

        If virtual user has a temporary home directory,
        clean up the directory.
        """
        self._clean_up_workspace_dir()
        super().stop(now=now)

    def _clean_up_workspace_dir(self):
        """ Clean up the virtual user's temporary directory, if exists
        """
        if not self._virtual_workspace:
            return

        # Clean up the directory
        # Make sure the temporary directory is not /, ./ or ../
        if self._virtual_workspace.strip('/') in ('', '.', '..'):
            self.log.warning("Virtual workspace is '%s'.  Seriously? "
                             "Not removing.", self._virtual_workspace)
        else:
            self.log.info('Removing %s ...', self._virtual_workspace)

            try:
                shutil.rmtree(self._virtual_workspace)
            except Exception as exception:
                self.log.error("Failed to remove %s, error %s",
                               self._virtual_workspace, str(exception))
