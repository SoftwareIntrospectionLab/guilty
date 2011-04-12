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

from repositoryhandler.backends import (create_repository, create_repository_from_path,
                                        RepositoryUnknownError, RepositoryCommandError)
from repositoryhandler.backends.watchers import LS, BLAME
from parser import create_parser, ParserUnknownError
from outputdevs import create_output_device, OutputDeviceError, OutputDeviceUnknownError
from optparse import OptionParser, Values
from utils import uri_is_remote, uri_to_filename, svn_uri_is_file, printerr, read_from_stdin
from _config import *
import os, sys
from Config import Config

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
    try:
        repo.blame (os.path.join (uri, filename),
                    rev = opts.revision,
                    mc = not opts.fast)
    except RepositoryCommandError, e:
        printerr ("Error getting blame information of path '%s': %s", (filename, e.error))
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

def split_filename_path (repo, path):
    if repo.get_type () == 'git':
        root = path
        while not os.path.isdir (os.path.join (root, ".git")):
            root = os.path.dirname (root)
        filename = path[len (root):].strip ('/')
    else:
        root = os.path.dirname (path)
        filename = os.path.basename (path)

    return root, filename

def main (args):
    parser = OptionParser (usage='%prog [ options ... ] URI [ FILES ]',
                           description='Analyze repository modifications',
                           version=VERSION)
    parser.disable_interspersed_args()
    parser.add_option ('-g', '--debug', dest='debug',
                       action="store_true", default=False,
                       help="Run in debug mode")
    parser.add_option ('-c', '--config-file', dest='config_file',
                       metavar='FILE',
                       help="Use a custom configuration file")
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

    # Save default values and pass an emtpy Values object to
    # parser_args, so that default values are not set. We need it
    # to know whether a value has been provided by the user or not
    # After parsing the command line we complete the config options
    # with the default values for the options that have not been set
    # by the parser or by a config file
    defaults = parser.get_default_values ()
    options, args = parser.parse_args (args, values = Values())

    try:
        config = Config (options.config_file)
    except AttributeError:
        config = Config ()

    config.update (options.__dict__)
    config.add (defaults.__dict__)

    if not args:
        parser.error("missing required repository URI")
        return 1

    parser.destroy ()

    if config.debug:
        import repositoryhandler.backends
        repositoryhandler.backends.DEBUG = True

    uri = args[0]
    files = args[1:]
    files_from_stdin = (files and files[0] == '-')

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
        out = create_output_device (config.output)
    except OutputDeviceUnknownError:
        printerr ("Output type %s is not supported by guilty", (config.output,))
        return 1
    except OutputDeviceError, e:
        printerr (str(e))
        return 1
    except Exception, e:
        printerr ("Unknown error creating output %s: %s", (config.output, str(e)))
        return 1

    try:
        out.begin (path or uri)
    except OutputDeviceError, e:
        printerr (str(e))
        return 1

    if files_from_stdin:
        read_from_stdin (blame, (repo, path or uri, out, config))
    elif files:
        for file in files:
            blame (file, (repo, path or uri, out, config))
    elif path and os.path.isfile (path):
        root, filename = split_filename_path (repo, path)
        blame (filename, (repo, root, out, config))
    elif not path and svn_uri_is_file (uri):
        blame (os.path.basename (uri), (repo, os.path.dirname (uri), out, config))
    else:
        if repo.get_type () == 'cvs':
            # CVS ls doesn't build the paths,
            # so we have to do it before calling blame
            cdir = [""]
            repo.add_watch (LS, cvs_proxy_blame, (repo, path or uri, out, config, cdir))
        elif repo.get_type () == 'git':
            # In git paths are relative to the root
            # we want paths relative to the provided uri
            repo.add_watch (LS, git_proxy_blame, (repo, path or uri, out, config))
        else:
            repo.add_watch (LS, blame, (repo, path or uri, out, config))
        repo.ls (path or uri, config.revision)

    out.end ()

    return 0
