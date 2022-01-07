if [ "${0:0:1}" = '/' ]; then
    SCRIPT_DIR=`dirname "$0"`
else
    cwd=`pwd`
    SCRIPT_DIR=`dirname "$cwd/$0"`
fi
export PATH=$SCRIPT_DIR/../node_modules/.bin/:$PATH
jupyterhub --ssl-key test.key --ssl-cert test.crt --debug
