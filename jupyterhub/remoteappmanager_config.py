# # --------------------
# # Docker configuration
# # --------------------
# #
# # Configuration options for connecting to the docker machine.
# # These options override the default provided by the local environment
# # variables.
# #
# # The endpoint of the docker machine, specified as a URL.
# # By default, it is obtained by DOCKER_HOST envvar. On Linux in a vanilla
# # install, the connection uses a unix socket by default.
#
# docker_host = "tcp://192.168.99.100:2376"

# # Docker realm is used to identify the containers that are managed by this
# # particular instance of simphony-remote. It will be the first entry in
# # the container name, and will also be added as part of a run-time container
# # label. You generally should not change this unless you have multiple
# # installations of simphony-remote all using the same docker host.
#
# docker_realm = "whatever"
#
# # TLS configuration
# # -----------------
# #
# # Set this to True to enable TLS connection with the docker client
#
# tls = True
#
# # Enables verification of the certificates. By default, this is the
# # result of the DOCKER_TLS_VERIFY envvar. Set to False to skip verification/
#
# tls_verify = True
#
# # Full paths of the CA certificate, certificate and key of the docker
# # machine. Normally these are computed from the DOCKER_CERT_PATH.
# # If you want to use a recognised CA for verification, set the tls_ca to
# # an empty string
#
# tls_ca = "/path/to/ca.pem"
# tls_cert = "/path/to/cert.pem"
# tls_key = "/path/to/key.pem"
#
# # ----------
# # Accounting
# # ----------
# # Notes on os.path:
# #  1. When running with system-user mode, both the current directory and '~'
# #  are the system user's home directory.
# #  2. When running in virtual-user mode, the current directory is the
# #  directory where jupyterhub is started, '~' would be evaluated according to
# #  the spawned process's owner's home directory (not the virtual user's
# #  home directory)
#
# # CSV database support
#
# database_class = "remoteappmanager.db.csv_db.CSVDatabase"
# database_kwargs = {
#     "csv_file_path": os.path.abspath("./remoteappmanager.csv")}
#
# # Sqlite database support
#
# database_class = "remoteappmanager.db.orm.ORMDatabase"
# database_kwargs = {
#     "url": "sqlite:///"+os.path.abspath('./remoteappmanager.db')}

# # ----------------
# # Google Analytics
# # ----------------
# # Put your tracking id from Google Analytics here.
# ga_tracking_id = "UA-XXXXXX-X"
