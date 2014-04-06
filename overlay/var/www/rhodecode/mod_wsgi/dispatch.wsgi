import os
os.environ["HGENCODING"] = "UTF-8"
os.environ['PYTHON_EGG_CACHE'] = '/var/www/rhodecode/data/.egg-cache'

# sometimes it's needed to set the current dir
os.chdir('/var/www/rhodecode/')

import site
site.addsitedir("/var/www/rhodecode/venv/lib/python2.7/site-packages")

from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

fileConfig('/var/www/rhodecode/production.ini')
application = loadapp('config:/var/www/rhodecode/production.ini')
