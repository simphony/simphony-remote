Administration
==============

As specified in the configuration section, the authenticator will grant additional
administrative rights to users in the specified set.

Once logged in, an administrative user will have the option to spawn an "Admin" session,
providing them with a different application, where they can add or remove users,
applications, and authorize users to run specific applications. It is also possible to stop currently running containers

It is important to note that the administrative interface works only with
accounting backends supporting addition and removal. More specifically, it
does not support the CSV backend. Read operations are supported, but write
operations will be denied.
