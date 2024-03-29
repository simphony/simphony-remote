import os
import escapism
import string

from traitlets import Any, Unicode, default
from tornado import gen

from jupyterhub.spawner import LocalProcessSpawner

ADMIN_CMD = "remoteappadmin"
USER_CMD = "remoteappmanager"


class BaseSpawner(LocalProcessSpawner):
    """Base class that provides common infrastructure to
    the actual spawners
    """

    #: The instance of the JupyterHub Proxy.
    #: We use Any in agreement with base class practice.
    proxy = Any()

    #: The path of the configuration file for the cmd executable
    config_file_path = Unicode(config=True)

    @property
    def cmd(self):
        """Overrides the base class traitlet so that we take full control
        of the spawned command according to user admin status"""
        return self.user_options.get('cmd', self._default_cmd())

    def __init__(self, **kwargs):
        super(BaseSpawner, self).__init__(**kwargs)
        # We can obtain a reference to the JupyterHub.proxy object
        # through the tornado settings passed onto the User
        self.proxy = self.user.settings.get('proxy')

    @default("options_form")
    def _options_form_default(self):
        """ Gives admins the option of spawning either RemoteAppManager
        admin or user sessions
        """
        if self.user.admin:
            return """
            <div>
                <legend>Choose RemoteAppManager Session:</legend>
                <select id="session_form" name="session" size="2">
                    <option value="admin" selected>Admin</option>
                    <option value="user">User</option>
                </select>
            </div>
            """
        return ""

    def _default_cmd(self):
        return [ADMIN_CMD] if self.user.admin else [USER_CMD]

    def options_from_form(self, form_data):
        """ Attempt to extract session selection from HTML form and
        return default session if not available
        """
        cmd = self._default_cmd()
        if "session" in form_data:
            selected = form_data.pop("session")[0]
            cmd = [ADMIN_CMD] if selected == "admin" else [USER_CMD]
        return {'cmd': cmd}

    def get_args(self):
        args = super().get_args()

        # Handle no default IP value (removed in jupyterhub v0.8.0)
        if not self.ip:
            args.append('--ip="127.0.0.1"')

        args.append('--user="{}"'.format(
            self.user.name))

        args.append('--base-urlpath="{}"'.format(
            self.server.base_url))

        args.append('--hub-prefix={}'.format(
            self.hub.base_url))

        args.append("--cookie-name={}".format(
            self.hub.cookie_name))

        args.append("--proxy-api-url={}".format(
            self.proxy.api_url))

        args.append("--logout_url={}".format(
            self.authenticator.logout_url(
                self.hub.base_url)))

        if self.config_file_path:
            args.append("--config-file={}".format(self.config_file_path))

        args.append("--login_service={}".format(
            self.authenticator.login_service))

        return args

    def get_env(self):
        env = super().get_env()
        env["PROXY_API_TOKEN"] = self.proxy.auth_token
        env.update(_docker_envvars())
        return env


class SystemUserSpawner(BaseSpawner):
    """
    Start remoteappmanager as a local process for a system user.

    The user identifier of the process is set to be the system user.
    The current directory is set to the system user's home directory.
    """


class VirtualUserSpawner(BaseSpawner):
    ''' Start remoteappmanager as a local process for a virtual user.

    A virtual user is not recognised as a system user, even if the
    user's name conincide with an existing system user.  As a result,
    the user does not need to be a system user for this spawner.

    The user identifier and the current work directory of the spawned
    local process are the same as the one that is running jupyterhub.
    '''

    #: Directory in which temporary home directory for the virtual
    #: user is created.  No directory is created if this is not
    #: defined and HOME directory would not be available.
    workspace_dir = Unicode(config=True)

    #: The path to the temporary workspace directory
    _virtual_workspace = Unicode()

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

    def user_env(self, env):
        env['USER'] = self.user.name

        if self._virtual_workspace:
            env['HOME'] = self._virtual_workspace

        return env

    @gen.coroutine
    def start(self):
        """ Start the process and create the virtual user's
        temporary home directory if `workspace_dir` is set
        """

        # Create the temporary directory as the user's workspace
        if self.workspace_dir and not self._virtual_workspace:
            try:
                workspace = _user_workspace(self.workspace_dir, self.user.name)
                os.makedirs(workspace, 0o755, exist_ok=True)
                self._virtual_workspace = workspace
            except Exception as exception:
                # A whole lot of reasons why temporary directory cannot
                # be created. e.g. workspace_dir does not exist
                # the owner of the process has no write permission
                # for the directory, etc.
                msg = ("Failed to create temporary directory for '{user}' in "
                       "'{tempdir}'.  Temporary workspace would not be "
                       "available. Please assign the spawner's `workspace_dir`"
                       " to a directory path where it has write permission. "
                       "Error: {error}")
                # log as error to avoid ugly traceback
                self.log.error(
                    msg.format(user=self.user.name,
                               tempdir=self.workspace_dir,
                               error=str(exception)))
            else:
                self.log.info("Created %s's temporary workspace in: %s",
                              self.user.name, self._virtual_workspace)
        return (yield super().start())

    @gen.coroutine
    def stop(self, now=False):
        """ Stop the process

        If virtual user has a temporary home directory,
        clean up the directory.
        """
        yield super().stop(now=now)


def _docker_envvars():
    """Returns a dictionary containing the docker environment variables, if
    present. If not present, returns an empty dictionary"""
    env = {envvar: os.environ[envvar]
           for envvar in ["DOCKER_HOST",
                          "DOCKER_CERT_PATH",
                          "DOCKER_MACHINE_NAME",
                          "DOCKER_TLS_VERIFY"]
           if envvar in os.environ}

    return env


# Used by escape
_ESCAPE_SAFE_CHARS = set(string.ascii_letters + string.digits + '-.')
_ESCAPE_CHAR = '_'


# Note: copied from container_manager.py, but we want to keep the
# spawners module completely separated from the remoteappmanager.
def escape(s):
    """Trivial escaping wrapper for well established stuff.
    Works for containers, file names. Note that it is not destructive,
    so it won't generate collisions."""
    return escapism.escape(s, _ESCAPE_SAFE_CHARS, _ESCAPE_CHAR)


def _user_workspace(base_dir, user_name):
    """Returns the appropriate user workspace for the given username.
    Raises ValueError if the user_name is only spaces after basenaming.
    """

    name = os.path.basename(user_name).strip()
    if len(name) == 0:
        raise ValueError("User name is invalid")

    return os.path.join(base_dir, escape(name))
