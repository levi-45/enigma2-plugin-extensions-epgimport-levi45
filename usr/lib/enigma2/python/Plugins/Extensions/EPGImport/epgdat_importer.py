from __future__ import absolute_import, print_function

import os
import sys

from . import epgdat

# Hack to make this test run on Windows (where the reactor cannot handle files)
if sys.platform.startswith('win'):
	tmppath = '.'
	settingspath = '.'
else:
	tmppath = '/tmp'
	settingspath = '/etc/enigma2'


def getMountPoints():
	mount_points = []
	try:
		with open('/proc/mounts', 'r') as mounts:
			for line in mounts:
				parts = line.split()
				mount_point = parts[1]
				if os.path.ismount(mount_point) and os.access(mount_point, os.W_OK):
					mount_points.append(mount_point)
	except Exception as e:
		print("[EPGImport] Errore durante la lettura di /proc/mounts:", e)
	return mount_points


mount_points = getMountPoints()


class epgdatclass:
	def __init__(self):
		self.data = None
		self.services = None
		path = tmppath
		"""
		# for mount_point in mount_points:
			# if '/media' in mount_point:
				# path = mount_point
		"""
		if self.checkPath('/media/cf'):
			path = '/media/cf'
		if self.checkPath('/media/mmc'):
			path = '/media/mmc'
		if self.checkPath('/media/usb'):
			path = '/media/usb'
		if self.checkPath('/media/hdd'):
			path = '/media/hdd'
		self.epgfile = os.path.join(path, 'epg_new.dat')
		self.epg = epgdat.epgdat_class(path, settingspath, self.epgfile)

	def importEvents(self, services, dataTupleList):
		'''This method is called repeatedly for each bit of data'''
		if services != self.services:
			self.commitService()
			self.services = services
		for program in dataTupleList:
			if program[3]:
				desc = program[3] + '\n' + program[4]
			else:
				desc = program[4]
			self.epg.add_event(program[0], program[1], program[2], desc)

	def commitService(self):
		if self.services is not None:
			self.epg.preprocess_events_channel(self.services)

	def epg_done(self):
		try:
			self.commitService()
			self.epg.final_process()
		except:
			print("[EPGImport] Failure in epg_done")
			import traceback
			traceback.print_exc()
		self.epg = None

	def checkPath(self, path):
		f = os.popen('mount', "r")
		for lx in f.xreadlines():
			if lx.find(path) != - 1:
				return True
		return False

	def __del__(self):
		'Destructor - finalize the file when done'
		if self.epg is not None:
			self.epg_done()
