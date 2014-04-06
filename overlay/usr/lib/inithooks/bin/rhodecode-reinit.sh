#!/bin/bash -ex


APACHE_RUNNING=$(/etc/init.d/apache2 status > /dev/null; echo $?)
MYSQL_RUNNING=$(/etc/init.d/mysql status > /dev/null; echo $?)

# default variables
DB_NAME=rhodecode
INSTALL_DIR=/var/www/rhodecode/venv
INSTALL_BIN=$INSTALL_DIR/bin
RC_CONF=/var/www/rhodecode/production.ini
RC_URI=http://127.0.0.1

if [ "$APACHE_RUNNING" != "0" ]; then
    /etc/init.d/apache2 start
fi
if [ "$MYSQL_RUNNING" != "0" ]; then
    /etc/init.d/mysql start
fi

# load default repos into rhodecode
RC_APIKEY=$(mysql --defaults-extra-file=/etc/mysql/debian.cnf --database=$DB_NAME -sNe "SELECT api_key FROM users WHERE username='admin'")
$INSTALL_BIN/rhodecode-api --apikey="$RC_APIKEY" --apihost=$RC_URI rescan_repos remove_obsolete:TRUE

if [ "$APACHE_RUNNING" != "0" ]; then
    /etc/init.d/apache2 stop
fi
if [ "$MYSQL_RUNNING" != "0" ]; then
    /etc/init.d/mysql stop
fi

# generate whoosh index
$INSTALL_BIN/paster make-index $RC_CONF -f

# create pid directory for celeryd (bug with creating headless openvz patch)
mkdir -p /var/run/celeryd
chown www-data:www-data /var/run/celeryd
