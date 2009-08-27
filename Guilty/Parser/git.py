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

from Guilty.Parser import Parser, register_parser
from Guilty.Blame import BlameLine

import re
import datetime, time

class GitParser (Parser):

    line_pattern = re.compile ("^([^ ]+)[\t ]+([^ ]+)[\t ]+\((.+) ([0-9]+) \+[0-9][0-9][0-9][0-9][\t ]+([0-9]+)\)[\t ]+.*$")

    def _parse_line (self, line):
        if not line:
            return

        match = self.line_pattern.match (line)
        if not match:
            return

        bl = BlameLine ()
        bl.line = int (match.group (5))
        bl.rev = match.group (1)
        bl.author = match.group (3)
        bl.date = datetime.datetime (* (time.gmtime (int (match.group (4)))[0:6]))
        filename = match.group (2)
        if filename != self.filename:
            bl.file = filename

        self.out.line (bl)

register_parser ('git', GitParser)

if __name__ == '__main__':
    import sys, os
    from TextOutputDevice import TextOutputDevice
    from Command import Command

    filename = sys.argv[1]
    p = GitParser (filename)
    p.set_output_device (TextOutputDevice ())

    def feed (line):
        p.feed (line)

    cmdline = ['git', 'blame', '--root', '-l', '-t', '-f', '-M', '-C', os.path.basename (filename)]
    cmd = Command (cmdline, os.path.dirname (filename))
    cmd.run (parser_out_func = feed)

