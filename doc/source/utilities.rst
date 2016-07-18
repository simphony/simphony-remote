.. _utilities:

Utilities
=========

Simphony remote comes with two utility scripts::

  - *remoteappdb*: Allows to add new applications, create new users, and
    specify permissions between users and applications in a database. 
    It is targeted at system administrators.
  - *remoteapprest*: Allows to start, stop, inquire running containers
    from the command line.

Remoteappdb
-----------

The script is aimed at system administrators using the database (by default,
a sqlite database) to perform accounting of users and applications.

The database must be first initialized with the `init` command::

     remoteappdb --db=~/remoteappmanager.db init

Once initialized, the database content is ready to be configured.
New applications are registered with `app create`. The image name
must match the image name in docker::

     remoteappdb --db=~/remoteappmanager.db app create myimage

The option `--verify` can be used to validate the image name against
docker.

You can also create users with the `user create` command::
    
     remoteappdb --db=~/remoteappmanager.db user create myuser

An application will not be visible not can be started by a user
until permission is granted. To grant permission, use the `app grant`
command::

     remoteappdb --db=~/remoteappmanager.db app create myimage myuser

By default, this command will grant no special options. It is however
possible to specify a different running policy, like for example mounting
a common home directory, with the following options::

    --allow-home   Enable mounting of home directory
    --allow-view   Enable third-party visibility of the running container.
    --volume TEXT  Application data volume, format=SOURCE:TARGET:MODE, where
                   mode is 'ro' or 'rw'.

Note that you can grant access to the same application with multiple, different
policies. Each application and policy will appear as a separate option in the
user choice of runnable applications.

The script provides additional functionality to inquire the current state
of the database, such as listing the current users, applications, revoke 
permissions, remove applications and so on.

Remoteapprest
------------- 

This script is experimental and exploits the REST API provided by the server to
allow inquiring, starting, and stopping containers from the command line.

Before using the CLI, you need to authenticate against the jupyterhub server
with the `login` command::

    remoteapprest login http://jupyterhubserver.example/

You will be inquired about username and password. Once sucessfully logged in, 
your credentials will be stored in a file `.remoteapprest` in your home directory.
Note that your password will not be saved, only an authentication token.

Once logged in, you can inquire about the available applications by issuing::

    remoteapprest app available

Note that you don't need to specify the endpoint. This command will show you a list
of the available applications, preceded by a unique identifier::

    6dbe8e166c94b0b4b36a2d961586acc0: myapplication

This identifier can be used to start a new container, using the following command::

    remoteapprest app start 6dbe8e166c94b0b4b36a2d961586acc0

The application will run, and can be seen with::

    remoteapprest app running

    83c18fcd833595a571d556a5e6c253f8: myapplication

Which will show a different identifier for this running instance.
Finally, the application can be stopped using the `stop` command::

    remoteapprest app stop 83c18fcd833595a571d556a5e6c253f8

