# Copyright (C) 2007  GSyC/LibreSoft
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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
#

__all__ = [
        'Parser',
        'create_parser',
        'register_parser'
]

class ParserUnknownError (Exception):
    '''Unkown parser type'''

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

_parsers = {}
def register_parser (name, klass):
    _parsers[name] = klass

def _get_parser (name):
    error = None
    if name not in _parsers:
        try:
            __import__ ('Guilty.Parser.%s' % name)
        except ImportError, e:
            error = e

    if name not in _parsers:
        if error is None:
            error = 'unknown error'
        else:
            error = str(error)
        raise ParserUnknownError ('Parser type %s not registered: %s' % (name, error))

    return _parsers[name]

def create_parser (name, filename):
    klass = _get_parser (name)
    return klass (filename)

def test_parser (p, repo):
    from Guilty.OutputDevs import OutputDevice
    from repositoryhandler.backends import create_repository_from_path
    from repositoryhandler.backends.watchers import BLAME

    class TestOutputDev (OutputDevice):
        def __init__ (self):
            self.n_line = 0

        def start_file (self, filename):
            pass
        def end_file (self):
            pass

        def line (self, line):
            self.n_line = line.line
            print line

    p.set_output_device (TestOutputDev ())

    def feed (line, p):
        p.feed (line)
        if p.n_line != p.out.n_line:
            import sys
            print "Error: line mismatch %d - %d" % (p.n_line, p.out.n_line)
            sys.exit (1)

    repo.add_watch (BLAME, feed, p)
    repo.blame (p.filename)
