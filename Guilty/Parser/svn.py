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
import datetime

class SVNParser (Parser):

    line_pattern = re.compile ("^[\t ]+([0-9]+)[\t ]+(.*) (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d):(\d\d):(\d\d) ([+-]\d\d\d\d) .*$")

    def _parse_line (self, line):
        if not line:
            return

        match = self.line_pattern.match (line)
        if not match:
            return

        bl = BlameLine ()
        bl.line = self.n_line
        bl.rev = match.group (1)
        bl.author = match.group (2)
        bl.date = datetime.datetime (int (match.group (3)), int (match.group (4)), int (match.group (5)),
                                     int (match.group (6)), int (match.group (7)), int (match.group (8)))

        self.out.line (bl)

register_parser ('svn', SVNParser)

if __name__ == '__main__':
    import sys
    from repositoryhandler.backends import create_repository_from_path
    from Guilty.Parser import test_parser

    repo = create_repository_from_path (sys.argv[1])
    filename = sys.argv[1]
    p = SVNParser (filename)
    test_parser (p, repo)


