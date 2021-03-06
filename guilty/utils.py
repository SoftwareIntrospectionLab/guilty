# Copyright (C) 2009 LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors: Carlos Garcia Campos <carlosgc@libresoft.es>

import os
import sys
import re

from Config import Config
config = Config ()

def to_utf8 (string):
    if isinstance (string, unicode):
        return string.encode ('utf-8')
    elif isinstance (string, str):
        for encoding in ['ascii', 'utf-8', 'iso-8859-15']:
            try:
                s = unicode (string, encoding)
            except:
                continue
            break

        return s.encode ('utf-8')
    else:
        return string

def uri_is_remote (uri):
    match = re.compile ("^.*://.*$").match (uri)
    if match is None:
        return False
    else:
        return not uri.startswith ("file://")

def uri_to_filename (uri):
    if uri_is_remote (uri):
        return None

    if uri.startswith ("file://"):
        uri = uri[uri.find ("file://") + len ("file://"):]

    return os.path.abspath (uri)

def svn_uri_is_file (uri):
    from repositoryhandler.backends.svn import get_info

    try:
        type = get_info (uri)['node kind']
    except:
        return False

    return type != 'directory'

def printout (str = '\n', args = None):
    if args is not None:
        str = str % tuple (to_utf8 (arg) for arg in args)

    if str != '\n':
        str += '\n'
    sys.stdout.write (to_utf8 (str))
    sys.stdout.flush ()

def printerr (str = '\n', args = None):
    if args is not None:
        str = str % tuple (to_utf8 (arg) for arg in args)

    if str != '\n':
        str += '\n'
    sys.stderr.write (to_utf8 (str))
    sys.stderr.flush ()

def printdbg (str = '\n', args = None):
    if not config.debug:
        return
    printout ("DBG: " + str, args)

def read_from_stdin (cb = None, user_data = None):
    import select, errno

    read_set = [sys.stdin]

    data = ""
    while read_set:
        try:
            rlist, wlist, xlist = select.select (read_set, [], [], 0)
        except select.error, e:
            # Ignore interrupted system call, reraise anything else
            if e.args[0] == errno.EINTR:
                continue
            raise

        if sys.stdin in rlist:
            chunk = os.read (sys.stdin.fileno (), 1024)
            if not chunk:
                sys.stdin.close ()
                read_set.remove (sys.stdin)

            data += chunk
            while '\n' in data:
                pos = data.find ('\n')
                cb (data[:pos + 1], user_data)
                data = data[pos + 1:]

