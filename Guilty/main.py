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

from repositoryhandler.backends import create_repository, create_repository_from_path, RepositoryUnknownError
from repositoryhandler.backends.watchers import LS, BLAME
from Parser import create_parser, ParserUnknownError
from TextOutputDevice import TextOutputDevice
from optparse import OptionParser
from utils import uri_is_remote, uri_to_filename, printerr
import os

def blame (filename, args):
    repo, uri, out = args
    filename = filename.strip (' \n')

    p = create_parser (repo.get_type (), filename)
    p.set_output_device (out)

    def feed (line, p):
        p.feed (line)

    wid = repo.add_watch (BLAME, feed, p)
    repo.blame (os.path.join (uri, filename))
    p.end ()
    repo.remove_watch (BLAME, wid)

def main (args):
    parser = OptionParser (usage='%prog [ options ... ] URI [ FILES ]',
                           description='Analyze repository modifications')
    parser.disable_interspersed_args()
    parser.add_option ('-g', '--debug', dest='debug',
                       action="store_true", default=False,
                       help="Run in debug mode")
    parser.add_option ('-r', '--revision', dest='revision',
                       metavar='REV',
                       help='Revision to analyze (HEAD)')
    parser.add_option ('-f', '--fast', dest='fast',
                       action="store_true", default=False,
                       help="Run faster but moves and copies are not detected")

    options, args = parser.parse_args(args)

    if not args:
        parser.error("missing required repository URI")
        return 1

    if options.debug:
        import repositoryhandler.backends
        repositoryhandler.backends.DEBUG = True

    uri = args[0]
    files = args[1:]
    if files and files[0] == '-':
        # TODO: Read files from stdin
        pass

    # Create repository
    path = uri_to_filename (uri)
    if path is not None:
        try:
            repo = create_repository_from_path (path)
        except RepositoryUnknownError:
            printerr ("Path %s doesn't seem to point to a repository supported by guilty", (path,))
            return 1
        except Exception, e:
            printerr ("Unknown error creating repository for path %s (%s)", (path, str (e)))
            return 1
        uri = repo.get_uri_for_path (path)
    else:
        uri = uri.strip ('/')
        repo = create_repository ('svn', uri)
        # Check uri actually points to a valid svn repo
        if repo.get_last_revision (uri) is None:
            printerr ("URI %s doesn't seem to point to a valid svn repository", (uri,))
            return 1

    # Check we have a parser for the given repo
    try:
        p = create_parser (repo.get_type (), 'foo')
    except ParserUnknownError:
        printerr ("%s repositories are not supported by guilty (yet)", (repo.get_type (),))
        return 1
    except Exception, e:
        printerr ("Unknown error creating parser for repository %s (%s)", (repo.get_uri (), str (e)))
        return 1
    del p

    out = TextOutputDevice ()
    if files:
        for file in files:
            blame (file, (repo, path or uri, out))
    else:
        repo.add_watch (LS, blame, (repo, path or uri, out))
        repo.ls (path or uri)

    return 0
