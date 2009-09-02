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
from OutputDevs import create_output_device, OutputDeviceError, OutputDeviceUnknownError
from optparse import OptionParser
from utils import uri_is_remote, uri_to_filename, svn_uri_is_file, printerr
import os

def blame (filename, args):
    repo, uri, out, opts = args
    filename = filename.strip (' \n')

    if filename[-1] == '/':
        return

    p = create_parser (repo.get_type (), filename)
    p.set_output_device (out)

    def feed (line, p):
        p.feed (line)

    wid = repo.add_watch (BLAME, feed, p)
    repo.blame (os.path.join (uri, filename),
                rev = opts.revision,
                mc = not opts.fast)
    p.end ()
    repo.remove_watch (BLAME, wid)

def cvs_proxy_blame (filename, args):
    path = filename.strip (' \n')
    if not path:
        return

    repo, uri, out, opts, cdir = args
    if path[-1] == ':':
        cdir[0] = path[:-1]
        return

    if not cdir[0] or cdir[0] == '.':
        filename = path
    else:
        filename = os.path.join (cdir[0], path)

    if os.path.isdir (os.path.join (uri, filename)):
        return

    blame (filename, args[:-1])

def git_proxy_blame (filename, args):
    path = filename.strip (' \n')
    if not path:
        return

    repo, uri, out, opts = args

    root = uri
    while not os.path.isdir (os.path.join (root, ".git")):
        root = os.path.dirname (root)

    prefix = uri[len (root):]
    if prefix:
        filename = filename[len (prefix.strip ('/')):]

    blame (filename.strip ('/'), args)

def add_outputs_options (parser):
    thisdir = os.path.abspath (os.path.dirname (__file__))

    for fname in os.listdir (os.path.join (thisdir, 'OutputDevs')):
        name, ext = os.path.splitext (fname)
        if not ext == '.py':
            continue

        try:
            module = __import__ ("Guilty.OutputDevs.%s" % name, None, None, ['add_options'])
            module.add_options (parser)
        except ImportError:
            continue
        except AttributeError:
            continue

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
    parser.add_option ('-o', '--output', dest='output',
                       default = 'text',
                       help='Output type [text|db|xml|csv] (%default)')
    add_outputs_options (parser)

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

    try:
        out = create_output_device (options.output, options)
    except OutputDeviceUnknownError:
        printerr ("Output type %s is not supported by guilty", (options.output,))
        return 1
    except OutputDeviceError, e:
        printerr (str(e))
        return 1
    except Exception, e:
        printerr ("Unknown error creating output %s", (options.output,))
        return 1

    if files:
        for file in files:
            blame (file, (repo, path or uri, out))
    elif path and os.path.isfile (path):
        blame (os.path.basename (path), (repo, os.path.dirname (path), out, options))
    elif not path and svn_uri_is_file (uri):
        blame (os.path.basename (uri), (repo, os.path.dirname (uri), out, options))
    else:
        if repo.get_type () == 'cvs':
            # CVS ls doesn't build the paths,
            # so we have to do it before calling blame
            cdir = [""]
            repo.add_watch (LS, cvs_proxy_blame, (repo, path or uri, out, options, cdir))
        elif repo.get_type () == 'git':
            # In git paths are relative to the root
            # we want paths relative to the provided uri
            repo.add_watch (LS, git_proxy_blame, (repo, path or uri, out, options))
        else:
            repo.add_watch (LS, blame, (repo, path or uri, out, options))
        repo.ls (path or uri, options.revision)

    return 0
