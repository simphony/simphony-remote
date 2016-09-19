Docker timeouts
^^^^^^^^^^^^^^^

If the application is unable to connect to docker and timeouts with the following message

    Error while fetching server API version: HTTPSConnectionPool(host='192.168.99.100', port=2376): 
    Max retries exceeded with url: /version (Caused by 
    ConnectTimeoutError(<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0x106299518>, 
    'Connection to 192.168.99.100 timed out. (connect timeout=60)')). 

The likely problem is that your docker machine is not reachable. The most likely cause is that
you recently recreated your default docker machine, or the docker machine is no longer reachable.
Make sure that your docker environment (DOCKER_HOST environment variable) is compatible with the 
docker machine current ip address (`docker-machine ip`). If not, reconfigure your docker machine
environment with `eval $(docker-machine env)`.

Error when connecting to docker: Permission denied
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check if your `/var/run/docker.sock` is accessible and readable. The likely cause is
that your current user is not in the `docker` group. Fix this by running::

    sudo addgroup your_username docker

and then logging out and in again.
