# filesys.py
#
# Copyright (C) 2008 Fabian Knittel <fabian.knittel@avona.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import re
import logging
import os

logger = logging.getLogger('dyntftpd.fs')

class FileSystemStack(object):
	def __init__(self):
		self.file_systems = []

	def add_file_sys(self, file_sys):
		self.file_systems.append(file_sys)

	def get_path(self, path):
		fs_path = None
		for file_sys in self.file_systems:
			fs_path = file_sys.get_path(path)
			if fs_path.exists():
				return fs_path
		return fs_path

class SimulatedFileSystem(object):
	def __init__(self):
		self.handlers = []

	def add_handler(self, regex, handler_func):
		self.handlers.append((regex, handler_func))

	def get_path(self, path):
		return SimulatedFilePath(self, path)

class SimulatedFilePath(object):
	def __init__(self, file_sys, path):
		self.file_sys = file_sys

		if len(path) > 0 and path[0] != '/':
			path = '/' + path
		self.path = os.path.normpath(path)

		# Find matching handler and execute it.
		self.fileobj = None
		self.size = 0
		for regex, handler in self.file_sys.handlers:
			logger.debug('Matching %s against %s' % (regex, path))
			match = re.search(regex, path)
			if match is not None:
				fileobj, size = handler(self.path, match)
				if fileobj is not None:
					self.fileobj = fileobj
					self.size = size
					break
				else:
					logger.info("Matching handler failed to produce a file name.")

	def safe(self):
		"""There is no direct file-system access, so we're always sure that
		the path is safe. We'll catch any odd cases through the pattern
		matching."""
		return True

	def exists(self):
		return self.fileobj is not None

	def open_read(self):
		if self.fileobj is None:
			raise RuntimeError("Attempted to open simulated path that " \
					"does not exist")
		return self.fileobj

	def get_path(self):
		return self.path

	def get_full_path(self):
		return self.path

	def get_size(self):
		return self.size

	def __str__(self):
		return self.path

# vim:set ft=python ts=4:
