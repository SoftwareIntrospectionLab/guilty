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

import sys
import re

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
        return uri[uri.find ("file://") + len ("file://"):]

    return uri

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
    printout ("DBG: " + str, args)


