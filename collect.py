"""Command line tool to assemble pre-saved text with sequential tweets fetched

Example:
    python collect.py
"""
import os
import sys
import time
from bowie import twitter


LOCKFILE_PATH = './collect.py.LOCK'

# Check if lockfile exists
if os.path.exists(LOCKFILE_PATH):
    filetime = os.path.getmtime(LOCKFILE_PATH)
    if (filetime + (24)) < time.time():
        print('Removing lockfile created more than a day ago: %s; than continuing.' % os.path.realpath(LOCKFILE_PATH))
        try:
            os.remove(LOCKFILE_PATH)
        except BaseException as ex:
            print('Cannot remove lockfile: %s %s; aborting.\n' % (os.path.realpath(LOCKFILE_PATH), ex))
            sys.exit(103)
    else:
        print('Lockfile exists, created less than a day ago: %s; aborting.\n' % os.path.realpath(LOCKFILE_PATH))
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
