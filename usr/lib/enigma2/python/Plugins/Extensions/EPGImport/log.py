# logging for XMLTV importer
#
# One can simply use
# import log
# print("Some text", file=log)
# because the log unit looks enough like a file!

from __future__ import absolute_import

import sys
import threading
try:  # python2 only
	from cStringIO import StringIO
except:  # both python2 and python3
	from io import StringIO

logfile = StringIO()
# Need to make our operations thread-safe.
mutex = threading.Lock()


def write(data):
	mutex.acquire()
	try:
		if logfile.tell() > 1000000:
			logfile.write("")
		logfile.write(data + '\n')
	finally:
		mutex.release()
	sys.stdout.write(data)


def getvalue():
	mutex.acquire()
	try:
		pos = logfile.tell()
		head = logfile.read()
		# logfile.seek(0, 0)
		logfile.write("")
		tail = logfile.read(pos)
	finally:
		mutex.release()
	return head + tail
