# boot_label.py
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

import textwrap

class BootLabel(object):
	SPACES = '        '

	def __init__(self, name, desc = None, default = False, help = None,
			disabled = False, password = None, indent = None):
		self.name = name
		self.desc = desc
		self.default = default
		self.help = help
		self.disabled = disabled
		self.password = password
		self.indent = indent

	def dump(self):
		"""Template method for sub-classes. Dumps specific label data."""
		return ''

	def __str__(self):
		str = "LABEL %s\n" % self.name
		if self.desc is not None:
			str += self.SPACES + "MENU LABEL %s\n" % self.desc
		if self.indent is not None:
			str += self.SPACES + "MENU INDENT %d\n" % self.indent
		if self.password is not None:
			str += self.SPACES + "MENU PASSWD %s\n" % self.password
		if self.help is not None:
			str += self.SPACES + "TEXT HELP\n"
			str += textwrap.fill(self.help, initial_indent = self.SPACES,
					subsequent_indent = self.SPACES) + "\n"
			str += self.SPACES + "ENDTEXT\n"
		str += self.dump()
		if self.disabled:
			str += self.SPACES + "MENU DISABLE\n"
		elif self.default:
			str += self.SPACES + "MENU DEFAULT\n"
		str += "\n"
		return str

class SeparatorBootLabel(BootLabel):
	def __init__(self, name = '', disabled = True, **kwargs):
		BootLabel.__init__(self, name, disabled = disabled, **kwargs)

	def __str__(self):
		str = "MENU SEPARATOR\n\n"
		str += BootLabel.__str__(self)
		return str

class LocalBootLabel(BootLabel):
	def dump(self):
		return self.SPACES + "localboot 0\n"

class ChainBootLabel(BootLabel):
	def __init__(self, name, hd, part, **kwargs):
		BootLabel.__init__(self, name, **kwargs)
		self.hd = hd
		self.part = part

	def dump(self):
		str = self.SPACES + "KERNEL chain.c32\n"
		str += self.SPACES + "APPEND %s %d\n" % (self.hd, self.part)
		return str

class ELFBootLabel(BootLabel):
    def __init_(self, name, kernel, append = None, **kwargs):
        BootLabel.__init__(self, name, **kwargs)
        self.kernel = kernel
        self.append = append

    def dump(self):
        str = self.SPACES + "KERNEL %s\n" % self.kernel
        if self.append:
            str += self.SPACES + "APPEND %s\n" % self.append
        return str

class LinuxBootLabel(BootLabel):
	def __init__(self, name, kernel, initrd, append, **kwargs):
		BootLabel.__init__(self, name, **kwargs)
		self.kernel = kernel
		self.initrd = initrd
		self.append = append

	def dump(self):
		str = self.SPACES + "KERNEL %s\n" % self.kernel
		str += self.SPACES + "APPEND initrd=%s %s\n" % (self.initrd,
				self.append)
		return str

class LinuxNfsRootBootLabel(LinuxBootLabel):
	def __init__(self, name, kernel, initrd, append, nfsroot,
			ramdisk_size = 14332, **kwargs):
		append = "ramdisk_size=%d root=/dev/nfs nfsroot=%s ip=dhcp %s" % \
				(ramdisk_size, nfsroot, append)
		LinuxBootLabel.__init__(self, name, kernel, initrd, append, **kwargs)

# vim:set ft=python ts=4 noet:
