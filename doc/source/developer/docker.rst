Docker image specifications
===========================

Docker images compliant to the simphony-remote application define a protocol
through docker LABEL and environment variables.

Labels
------

Labels are defined with the prefix namespace::

    eu.simphony-project.docker

The following labels are currently defined. 
Their definition can be found in `remoteappmanager.docker.docker_labels`

    - `ui_name`: the UI visible name of the image
    - `icon_128`: a base64 encoded png image that will result as an icon
    - `description`: a user-readable description of the image
    - `type`: a string identifying the type of the container, depending on
      the original base image (vncapp or webapp)
    - `env`: subnamespace for accepted environment variables. See below.

The env is a subnamespace defining the environment variables the image internals 
can understand.  This does not mean that they are the only ones that will be
passed to the image. 

The naming strategy works around the `docker label restrictions 
<https://docs.docker.com/engine/userguide/labels-custom-metadata/#/label-keys-namespaces>`_ 
of having `kebab case <http://c2.com/cgi/wiki?KebabCase>`_ vs envvars that are
traditionally MACRO_CASE. Additionally, it allows new variables to be added
by layers without having to know the variables understood by the base layer.

The strategy is as follows: the name after the `env` will be converted to uppercase
and dashes converted to underscores. For example:

   `env.x11-width` -> container accepts and understands envvar `X11_WIDTH`

the value of the label is currently unused, and should be left empty.

If your application uses variables with a different convention, or uses double underscores,
you will have to define an auxilliary variable and transfer the value in the image 
startup scripts.

Currently reserved env keys:

    - `x11-width`: for the VNC images, the X11 width
    - `x11-height`: for the VNC images, the X11 height
    - `x11-depth`: for the VNC images, the X11 depth (currently unused, fixed at 16)

Container Labels
----------------

When a container is started, the following labels will be added:

    - `url_id`: unique identifier that ends up in the URL when the 
              user is redirected
    - `mapping_id`: a unique key identifying the combination of image 
                  and policy used to start the container.
    - `user`: the user that started the container

Environment variables
---------------------

The following environment variables are passed at container startup:

    `JPY_USER`: the username used to login to the Jupyterhub frontend.
                Can be an email address, or anything else your 
                authenticator accepts.
    `JPY_BASE_USER_URL`: The base URL _path_ where the user has its service.
    `USER`: A unix-likable username to create the container user.
    `URL_ID`: a unique key assigned to the container that will end up in
              the user-exposed URL to reach the container.

If the image accepts additional envvars (through the env labels mechanism outlined above)
these variables will be passed through the configurables mechanism: special variables
are recognized and exposed to the user as a configurable UI, then passed to the container
at startup. See the reserved `env` labels for details.

