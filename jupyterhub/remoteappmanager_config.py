import os
import platform

# Clarifies to be not intended to be passed to tornado config conflict.
# Tornado extracts vars from global scope of the config file.
_platform = platform.system()

if _platform == 'Darwin':
    # For platforms that have a separate docker machine, we need to connect
    # using tls, but if we use self-signed certificates, using tls as True
    # will produce an error of incorrect CA validation.
    # As a consequence, we set tls to false, and tls_verify to true, honoring
    # docker documentation (although not very clear on this point)
    # See https://docs.docker.com/engine/security/https/
    if "DOCKER_CERT_PATH" not in os.environ:
        raise ValueError("Docker environment has not been defined.")

    tls = False
    tls_verify = bool(int(os.path.expandvars("${DOCKER_TLS_VERIFY}")))
    tls_ca = os.path.expandvars('${DOCKER_CERT_PATH}/ca.pem')
    tls_cert = os.path.expandvars('${DOCKER_CERT_PATH}/cert.pem')
    tls_key = os.path.expandvars('${DOCKER_CERT_PATH}/key.pem')
    docker_host = os.path.expandvars("${DOCKER_HOST}")
elif _platform == 'Linux':
    # Linux works through unix socket, so we don't need tls.
    tls = False
else:
    raise RuntimeError("Unknown platform {}".format(_platform))


# Define the sqlalchemy url for the database.
# Notes:
# 1. this database is shared among all instances of the remoteappmanager.
# 2. When running with system-user mode, the jupyterhub spawners spawn in
#    the user's home directory; when running in virtual-user mode,
#    the current directory is the directory where jupyterhub is started
# 3. '~' would be evaluated as the spawned user's home directory
db_url = "sqlite:///"+os.path.abspath("./remoteappmanager.db")
