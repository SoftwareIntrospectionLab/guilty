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

if __name__ == '__main__':
    import sys
    sys.path.insert (0, '../../')

from Guilty.Parser import Parser, register_parser
from Guilty.Blame import BlameLine

import re
import datetime, time

class CVSParser (Parser):

    line_pattern = re.compile ("^([\d\.]*)[\t ]+\(([^\t ]+)[\t ]+(\d\d-[A-Z][a-z][a-z]-\d\d)\):.*$")

    def __init__ (self, filename):
        Parser.__init__ (self, filename)

        self.bline = 1

    def _parse_line (self, line):
        if not line:
            return

        match = self.line_pattern.match (line)
        if not match:
            return

        bl = BlameLine ()
        bl.line = self.bline
        bl.rev = match.group (1)
        bl.author = match.group (2)
        bl.date = datetime.datetime (* (time.strptime (match.group (3), "%d-%b-%y")[0:3]))

        self.bline += 1
        self.out.line (bl)

register_parser ('cvs', CVSParser)

if __name__ == '__main__':
    import sys, os
    from Guilty.TextOutputDevice import TextOutputDevice
    from Guilty.Command import Command

    filename = sys.argv[1]
    p = CVSParser (os.path.basename (filename))
    p.set_output_device (TextOutputDevice ())

    def feed (line):
        p.feed (line)

    cmdline = ['cvs', 'annotate', os.path.basename (filename)]
    cmd = Command (cmdline, os.path.dirname (filename))
    cmd.run (parser_out_func = feed)

