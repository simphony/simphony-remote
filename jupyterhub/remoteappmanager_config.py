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
    tls = False
    tls_verify = True
    tls_ca = os.path.expanduser('~/.docker/machine/machines/default/ca.pem')
    tls_cert = os.path.expanduser(
        '~/.docker/machine/machines/default/cert.pem')
    tls_key = os.path.expanduser('~/.docker/machine/machines/default/key.pem')
    docker_host = "tcp://192.168.99.100:2376"
elif _platform == 'Linux':
    # Linux works through unix socket, so we don't need tls.
    tls = False
else:
    raise RuntimeError("Unknown platform {}".format(_platform))


# Define the sqlalchemy url for the database.
# Note that this database is shared among all instances of the
# remoteappmanager.
db_url = "sqlite:///remoteappmanager.db"
