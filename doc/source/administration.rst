Administration
==============

As specified in the configuration section, the authenticator will grant additional
administrative rights to users in the specified set.

Once logged in, an administrative user will have the option to spawn an "Admin" session,
providing them with a different application, where they can add or remove users,
applications, and authorize users to run specific applications. It is also possible to stop
currently running containers

    **NOTE**: the existing "Admin" or "User" session must be shut down before the options form
    will be shown again. This is a JupyterHub-level operation and is not automatically performed
    upon logging out. Therefore it must be manually carried out by either navigating to
    ``https://<simphony-remote>/hub/admin`` or ``https://<simphony-remote>/hub/home`` whilst logged
    in and selecting the appropriate the "Stop My Sever" option.

It is important to note that the administrative interface works only with
accounting backends supporting addition and removal. More specifically, it
does not support the CSV backend. Read operations are supported, but write
operations will be denied.
