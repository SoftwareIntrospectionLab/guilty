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

class BlameLine:
    def __init__ (self):
        self.__dict__ = { 'line'   : None,
                          'rev'    : None,
                          'author' : None,
                          'date'   : None,
                          'file'   : None }

    def __getinitargs__(self):
        return ()

    def __getstate__(self):
        return self.__dict__

    def __setstate__ (self, dict):
        self.__dict__.update (dict)

    def __getattr__ (self, name):
        return self.__dict__[name]

    def __setattr__ (self, name, value):
        self.__dict__[name] = value

    def __str__ (self):
        return "BlameLine %r" % (self.__dict__)

    def __repr__ (self):
        return "BlameLine %r" % (self.__dict__)

    def __eq__ (self, other):
        return isinstance (other, BlameLine) and self.line == other.line

    def __ne__ (self, other):
        return not isinstance (other, BlameLine) or self.line != other.line
