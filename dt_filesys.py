# filesys.py
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

import re
import logging
import os
import tftpy

logger = logging.getLogger('dyntftpd.fs')

class FileSystemStack(object):
    def __init__(self):
        self.file_systems = []

    def add_file_sys(self, file_sys, base_path='/', case_sensitive=True):
        base_path = os.path.normpath(base_path)
        # The base_path should end with a slash.
        if not base_path.endswith('/'):
            base_path += '/'
        self.file_systems.append((file_sys, base_path, case_sensitive))

    @staticmethod
    def _get_sub_path(base_path, path, case_sensitive):
        """Determines whether 'base_path' is the base path of 'path'.  If it
        is, the path beyond the base path is returned.  Returns None for
        non-matching paths.

        If 'case_sensitive' is False, the base path matching is
        case-insensitive. However, the returned sub path's case is correctly
        maintained.
        """
        path = os.path.normpath(path)
        if case_sensitive:
            if not path.startswith(base_path):
                return None
        else:
            if not path.lower().startswith(base_path.lower()):
                return None
        return path[len(base_path) - 1:]

    def get_path(self, path):
        for file_sys, base_path, case_sensitive in self.file_systems:
            sub_path = self._get_sub_path(base_path, path, case_sensitive)
            logger.debug('base_path %s, path %s, sub_path %s' % (base_path,
                    path, sub_path))
            if sub_path is not None:
                fs_path = file_sys.get_path(sub_path)
                if fs_path is not None:
                    return fs_path
        return None

class SanitiseRequestFileSystemFilter(object):
    def __init__(self, fs):
        self._fs = fs

    def get_path(self, path):
        path = path.replace('\\', '/')
        if not path.startswith('/'):
            path = '/' + path
        return self._fs.get_path(path)

class SimulatedFileSystem(object):
    def __init__(self):
        self.handlers = []

    def add_handler(self, regex, handler_func):
        self.handlers.append((regex, handler_func))

    def get_path(self, path):
        if len(path) > 0 and path[0] != '/':
            path = '/' + path
        path = os.path.normpath(path)

        # Find matching handler and execute it.
        for regex, handler in self.handlers:
            logger.debug('Matching %s against %s' % (regex, path))
            match = re.search(regex, path)
            if match is not None:
                fileobj, size = handler(path, match)
                if fileobj is not None:
                    return SimulatedFilePath(path, fileobj, size)
                    break
                else:
                    logger.info("Path '%s' matched handler's regex '%s', but " \
                            "handler came back empty." % (path, regex))
        return None

class SimulatedFilePath(object):
    def __init__(self, path, fileobj, size):
        self.path = path
        self.fileobj = fileobj
        self.size = size

    def open_read(self):
        return self.fileobj

    def get_path(self):
        return self.path

    def get_size(self):
        return self.size

    def __str__(self):
        return self.path

def find_case_insensitive_path(base_path, path):
    full_path = base_path
    real_path = ''
    logger.debug('base_path: %s, path: %s' % (base_path, path))
    for path_part in path.split('/'):
        if path_part == '':
            continue
        path_part = path_part.lower()
        precise_path_part = None
        if os.path.exists(os.path.join(base_path, real_path, path_part)):
            # There's a case sensitive match, we prefer that.
            precise_path_part = path_part
        else:
            for fn in os.listdir(full_path):
                if fn.lower() == path_part:
                    # We found a matching path part.
                    precise_path_part = fn
                    break
        if precise_path_part is not None:
            real_path = os.path.join(real_path, precise_path_part)
            full_path = os.path.abspath(os.path.join(base_path, real_path))
        else:
            # There were no matches for this component.
            logger.debug('  no match for component %s' % (path_part))
            return None
    logger.debug('real_path: %s' % real_path)
    return real_path

class CaseInsensitiveFileSys(tftpy.TftpNativeFileSys):
    def get_path(self, path):
        """Walks the path and searches for path elements that match the
        requested path, but does so in a case insensitive way.
        """
        real_path = find_case_insensitive_path(self.root, path)
        if real_path is None:
            # There is no such file, even with case-insensitive search.
            return None
        if real_path != path:
            logger.info('case-translated requested path "%s" to "%s"' % (path,
                   real_path))
        return tftpy.TftpNativeFileSys.get_path(self, real_path)

# vim:set ft=python sw=4 et:
