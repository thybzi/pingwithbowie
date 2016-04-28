"""Command line tool to assemble pre-saved text with sequential tweets fetched

Example:
    python collect.py
"""
import os
import sys
from bowie import twitter


LOCKFILE_PATH = './collect.py.LOCK'

# Check if lockfile exists
if os.path.exists(LOCKFILE_PATH):
    print('Lockfile exists: %s; aborting.\n' % os.path.realpath(LOCKFILE_PATH))
    sys.exit(101)

# Create lockfile
try:
    open(LOCKFILE_PATH, 'w').close()
except BaseException as ex:
    print('Cannot create lockfile: %s %s; aborting.\n' % (os.path.realpath(LOCKFILE_PATH), ex))
    sys.exit(102)

# Start assemble process
twitter.assemble_collection()

# Remove lockfile when finished
os.remove(LOCKFILE_PATH)
