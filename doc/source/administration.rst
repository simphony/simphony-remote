Administration
==============

As specified in the deployment section, the authenticator will grant administrative
rights to users in the specified set. 
Once logged in, an administrative user will be served by a different application,
where it can add or remove users, applications, and authorize users to run specific
applications. It is also possible to stop currently running containers.

It is important to note that the administrative interface works only with
accounting backends supporting addition and removal. More specifically, it
does not support the CSV backend. Read operations are supported, but write
operations will be denied.
