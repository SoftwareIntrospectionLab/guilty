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

from guilty.outputdevs import OutputDevice, register_output_device
from guilty.config import Config

class XMLOutputDevice (OutputDevice):

    def begin (self, uri):
        rev = Config ().revision
        print '<?xml version="1.0"?>'
        print '<repository uri = "%s"' % (uri),
        if rev:
            print 'revision = "%s"' % (rev),
        print '>'

    def start_file (self, filename):
        print '\t<file path = "%s">' % (filename)

    def line (self, line):
        if line.file:
            orig_file = ' orig_file = "%s" ' % (line.file)
        else:
            orig_file = ' '
        print '\t\t<line n = %d revision = "%s" author = "%s" date = "%s"%s/>' % \
            (line.line, line.rev, line.author, line.date, orig_file)

    def end_file (self):
        print '\t</file>'

    def end (self):
        print '</repository>'

register_output_device ('xml', XMLOutputDevice)
