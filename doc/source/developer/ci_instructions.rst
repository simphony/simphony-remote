Docker CI for SimPhoNy-Remote
=============================

This module contains Docker files that can be used to test installations
for various platforms.

Please ensure that you are building from a clean repository, since all contents will be copied into the Docker
image and may affect the build. For example, if a ``venv`` is already present then this will prevent the
Python virtual environment inside the container from being set up correctly.

However, running S-R as a Docker container image is NOT fully supported for deployment, since image applications
will not be able to be run.


Building SimPhoNy-Remote as a Docker Image
------------------------------------------

It is also possible to build SimPhoNy-Remote as a Docker container image using a `Dockerfile` script
provided for either `ubuntu` or `centos` Linux OS::

    docker build . --file Dockerfile-<linux os> -t simphony-remote

Alternatively, you can provide the following `docker-compose` command::

    docker-compose build simphony-remote-<linux os>

Running SimPhoNy-Remote as a Docker Image
-----------------------------------------

When running, S-R needs to be given a reference to the Docker daemon that contains the applications
(also Docker container images) required by the Hub session. Running Docker inside Docker is not recommended,
but there are a couple of approaches that can be used as a work around, such as
`sharing volumes <https://docs.docker.com/storage/volumes>`_ or performing a
`bind mount <https://docs.docker.com/storage/bind-mounts>`_.

We have successfully ran a S-R session using a Docker container image by sharing volumes with the following command::

    docker run -it -v /var/run/docker.sock:/var/run/docker.sock -p 8000:8000 simphony-remote-<linux os> bash

This will allow a jupyterhub session with user login / management services to be initiated as normal. However, as
stated previously, any S-R applications will not be able to run.
