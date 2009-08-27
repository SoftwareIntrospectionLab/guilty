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

class Parser:

    def __init__ (self, filename):
        self.filename = filename
        self.n_line = 0
        self.handler = None

    def set_output_device (self, out):
        self.out = out
        out.start_file (self.filename)

    def _parse_line (self):
        raise NotImplementedError

    def feed (self, data):
        for line in data.splitlines ():
            self.n_line += 1
            self._parse_line (line)

    def end (self):
        if not self.filename:
            return
        self.out.end_file ()
        self.filename = None
