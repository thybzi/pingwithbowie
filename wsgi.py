#!/usr/bin/python
import os
virtenv = os.path.join(os.environ.get('OPENSHIFT_PYTHON_DIR', '.'), 'virtenv')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

# Run flask application
from bowie import app as application
if __name__ == '__main__':
    application.run(debug=True)
