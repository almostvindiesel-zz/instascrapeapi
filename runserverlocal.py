print "Loading runserverlocal.py ..."

import os
os.environ['NOMNOMTES_ENVIRONMENT'] = 'local'

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)