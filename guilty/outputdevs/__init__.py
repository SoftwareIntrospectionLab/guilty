# Copyright (C) 2009  GSyC/LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Carlos Garcia Campos <carlosgc@libresoft.es>
#

__all__ = [
    'OutputDevice',
    'create_output_device',
    'register_output_device'
]

class OutputDeviceError (Exception):
    '''Generic OutputDeviceError'''

class OutputDeviceUnknownError (Exception):
    '''Unknown output device type'''

class OutputDevice:

    def begin (self, uri):
        pass

    def start_file (self, filename):
        raise NotImplementedError

    def line (self, line):
        raise NotImplementedError

    def end_file (self):
        raise NotImplementedError

    def end (self):
        pass

_devs = {}
def register_output_device (name, klass):
    _devs[name] = klass

def _get_output_device (name):
    error = None
    if name not in _devs:
        try:
            __import__ ('guilty.outputdevs.%s' % name)
        except ImportError, e:
            error = e

    if name not in _devs:
        if error is None:
            error = 'unknown error'
        else:
            error = str(error)
        raise OutputDeviceUnknownError ('Output type %s not registered: %s' % (name, error))

    return _devs[name]

def create_output_device (name):
    klass = _get_output_device (name)
    return klass ()
