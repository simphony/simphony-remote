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
#
# # TLS configuration
# # -----------------
# #
# # Set this to True only if your docker machine has a certificate signed by
# # a recognised CA.
# # If using self-signed certificates, using tls as True will produce an error
# # of incorrect CA validation. As a consequence, the default tls setting is
# # False, and tls_verify is according to the current environment (likely True
# # with default setup on OSX), honoring docker documentation.
# # See https://docs.docker.com/engine/security/https/ for additional details
#
# tls = True
#
# # Enables verification of the certificates. By default, this is the
# # result of the DOCKER_TLS_VERIFY envvar
#
# tls_verify = True
#
# # Full paths of the CA certificate, certificate and key of the docker
# # machine. Normally these are computed from the DOCKER_CERT_PATH
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
# accounting_class = "remoteappmanager.db.csv_db.CSVAccounting"
# accounting_kwargs = {
#     "csv_file_path": os.path.abspath("./remoteappmanager.csv")}
#
# # Sqlite database support
#
# accounting_class = "remoteappmanager.db.orm.AppAccounting"
# accounting_kwargs = {
#     "url": "sqlite:///"+os.path.abspath('./remoteappmanager.db')}
