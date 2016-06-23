import os
from remoteappmanager.docker.docker_client_config import DockerClientConfig


def nonlinux_config():
    """This configuration is used for typical non-linux cases
    where the connection must be through ssl and to a spawned
    virtual machine."""

    return DockerClientConfig(
        tls=False,
        tls_verify=True,
        tls_ca=os.path.expanduser('~/.docker/machine/machines/default/ca.pem'),
        tls_cert=os.path.expanduser(
            '~/.docker/machine/machines/default/cert.pem'),
        tls_key=os.path.expanduser(
            '~/.docker/machine/machines/default/key.pem'),
        docker_host="tcp://192.168.99.100:2376")
