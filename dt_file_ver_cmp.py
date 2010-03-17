# file_ver_cmp.py
#
# Copyright (C) 2008, 2010 Fabian Knittel <fabian.knittel@avona.com>
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

import os
import re

def split_ver(ver):
	return ver.split('-', 1)

def split_file_ver(base, suffix, name):
	"""Split off base and suffix from the file-name and return the file's
	version."""
	return name[len(base):-len(suffix)]

def cmp_maybe_int(val1, val2):
	"""Compare two string values. In case they're numeric, compare the
	numeric values, otherwise do a alphanumeric compare. In case only one of
	them is numeric, the numeric value wins.
	"""
	try:
		int_val1 = int(val1)
	except:
		int_val1 = None
	try:
		int_val2 = int(val2)
	except:
		int_val2 = None

	if int_val1 is not None or int_val2 is not None:
		return cmp(int_val1, int_val2)
	return cmp(val1, val2)

def cmp_dotted_ver(ver1, ver2):
	# Trivial case.
	if ver1 == ver2:
		return 0

	# Compare each component.
	vers1 = ver1.split('.')
	vers2 = ver2.split('.')
	i = 0
	while i < len(vers1) and i < len(vers2):
		if vers1[i] != vers2[i]:
			return cmp_maybe_int(vers1[i], vers2[i])
		i += 1

	# The longer version with otherwise equal components is the newer / higher
	# version.
	if len(vers1) > len(vers2):
		return 1
	else:
		return -1

def cmp_ver(ver1, ver2):
	# Trivial case.
	if ver1 == ver2:
		return 0

	front1, back1 = split_ver(ver1)
	front2, back2 = split_ver(ver2)
	# If the front version is equal, compare the appended version.
	if front1 == front2:
		return cmp_maybe_int(back1, back2)

	return cmp_dotted_ver(front1, front2)

def cmp_files(base, suffix, name1, name2):
	if name1 == name2:
		return 0
	ver1 = split_file_ver(base, suffix, name1)
	ver2 = split_file_ver(base, suffix, name2)
	return cmp_ver(ver1, ver2)

def highest_file_ver(base, suffix, files):
	highest_file = files[0]
	for file in files[1:]:
		if cmp_files(base, suffix, file, highest_file) == 1:
			highest_file = file
	return highest_file

def find_highest_file_ver(base, suffix, search_dir):
	regex = '^%s.+%s$' % (base, suffix)
	prog = re.compile(regex)
	files = filter(prog.search, os.listdir(search_dir))
	if len(files) > 0:
		return os.path.join(search_dir, highest_file_ver(base, suffix, files))
	else:
		return None

# vim:set ft=python ts=4 noet:
