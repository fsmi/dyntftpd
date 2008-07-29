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
			str += self.SPACES + "MENU PASSWORD %s\n" % self.password
		if self.help is not None:
			str += self.SPACES + "TEXT HELP\n"
			str += textwrap.fill(self.help, initial_indent = self.SPACES,
					subsequent_indent = self.SPACES) + "\n"
			str += self.SPACES + "END TEXT\n"
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
		print repr(kwargs)
		BootLabel.__init__(self, name, **kwargs)
		self.hd = hd
		self.part = part

	def dump(self):
		str = self.SPACES + "KERNEL chain.c32\n"
		str += self.SPACES + "APPEND %s %d\n" % (self.hd, self.part)
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

# vim:set ft=python ts=4:
