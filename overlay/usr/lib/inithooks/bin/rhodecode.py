#!/usr/bin/python
"""Set Rhodecode admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively

"""

import os
import sys
import getopt
import bcrypt
import hashlib
import random
import string
from tempfile import _RandomNameSequence

from dialog_wrapper import Dialog
from mysqlconf import MySQL

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Rhodecode Password",
            "Enter new password for the Rhodecode 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Rhodecode Email",
            "Enter email address for the Rhodecode 'admin' account.",
            "admin@example.com")
    
    # salt = "".join(random.choice(string.letters) for line in range(16))
    hashpass = bcrypt.hashpw(password, bcrypt.gensalt(10))

    salt = _RandomNameSequence().next()
    admin_apikey = hashlib.sha1('admin' + salt).hexdigest()
    salt = _RandomNameSequence().next()
    default_apikey = hashlib.sha1('default' + salt).hexdigest()

    m = MySQL()
    m.execute('UPDATE rhodecode.users SET email=\"%s\" WHERE username=\"admin\";' % email)
    m.execute('UPDATE rhodecode.users SET password=\"%s\" WHERE username=\"admin\";' % hashpass)
    m.execute('UPDATE rhodecode.users SET api_key=\"%s\" WHERE username=\"admin\";' % admin_apikey)
    m.execute('UPDATE rhodecode.users SET api_key=\"%s\" WHERE username=\"default\";' % default_apikey)

    script = os.path.join(os.path.dirname(__file__), 'rhodecode-reinit.sh')
    os.system(script)

if __name__ == "__main__":
    main()

