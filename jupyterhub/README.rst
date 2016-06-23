Jupyterhub
----------

The application in this repo is spawned by jupyterhub and
requires it to work. In particular, our application does not
provide css/js that are available in jupyterhub, and that
jupyterhub itself exports via its own webserver.

Start jupyterhub in this directory.

test.crt, test.key, and test.csr are self-signed certificates
that should only be used for testing. They are public because 
their security is not paramount. Use a properly secured 
(and possibly not self-signed) certificate for production 
execution.

