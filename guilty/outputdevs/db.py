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

from guilty.outputdevs import OutputDevice, register_output_device, OutputDeviceError
from optparse import OptionValueError
from guilty.utils import to_utf8, printdbg
from guilty.Config import Config

def _check_and_store (option, opt_str, value, parser):
    try:
        output = parser.values.output
    except AttributeError:
        raise OptionValueError ("database specific options must go after -o option")

    if output != 'db':
        raise OptionValueError ("invalid option %s for output %s" % (opt_str, output))

    setattr (parser.values, option.dest, value)

def add_options (parser):
    from optparse import OptionGroup

    group = OptionGroup (parser, "Database Options")
    group.add_option ('--db-driver', dest='db_driver', type=str,
                      action="callback", callback=_check_and_store,
                      default='mysql', metavar='driver',
                      help="Output database driver [mysql|sqlite] (%default)")
    group.add_option ('-u', '--db-user', dest='db_user', type=str,
                      action="callback", callback=_check_and_store,
                      default='operator', metavar='user',
                      help="Database user name (%default)")
    group.add_option ('-p', '--db-password', dest='db_password', type=str,
                      action="callback", callback=_check_and_store,
                      metavar='password',
                      help="Database user password")
    group.add_option ('-d', '--db-database', dest='db_database', type=str,
                      action="callback", callback=_check_and_store,
                      default='guilty', metavar='database',
                      help="Database name (%default)")
    group.add_option ('-H', '--db-hostname', dest='db_hostname', type=str,
                      action="callback", callback=_check_and_store,
                      default='localhost', metavar='host',
                      help="Name of the host where database server is running (%default)")
    parser.add_option_group (group)


class DatabaseException (Exception):
    '''Generic Database Exception'''
class DatabaseDriverNotSupported (DatabaseException):
    '''Database driver is not supported'''
class DatabaseNotFound (DatabaseException):
    '''Selected database doesn't exist'''
class AccessDenied (DatabaseException):
    '''Access denied to databse'''
class TableAlreadyExists (DatabaseException):
    '''Table alredy exists in database'''

class DBObject:

    def build_insert (self):
        query = "INSERT INTO %s (" % self.__table__
        fields = self.__dict__.keys ()
        query += ",".join (fields)
        query += ") values ("
        query += ",".join (['?']*len(fields))
        query += ")"

        args = [self.__dict__[field] for field in fields]

        return query, args

class DBFile (DBObject):
    id_counter = 1
    __table__ = 'files'

    def __init__ (self, path):
        self.id = DBFile.id_counter
        DBFile.id_counter += 1
        self.path = to_utf8 (path)

class DBAuthor (DBObject):
    id_counter = 1
    __table__ = 'authors'

    def __init__ (self, name):
        self.id = DBAuthor.id_counter
        DBAuthor.id_counter += 1
        self.name = to_utf8 (name)

class DBRevision (DBObject):
    id_counter = 1
    __table__ = 'revisions'

    def __init__ (self, rev):
        self.id = DBRevision.id_counter
        DBRevision.id_counter += 1
        self.revision = rev

class DBLine (DBObject):
    id_counter = 1
    __table__ = 'blame'

    def __init__ (self, n_line, date, orig_path = None):
        self.id = DBLine.id_counter
        DBLine.id_counter += 1
        self.line = n_line
        self.date = date
        if orig_path is not None:
            self.orig_path = to_utf8 (orig_path)

def statement (str, ph_mark):
    if "?" == ph_mark or "?" not in str:
        printdbg (str)
        return str

    tokens = str.split ("'")
    for i in range(0, len (tokens), 2):
        tokens[i] = tokens[i].replace ("?", ph_mark)

    retval = "'".join (tokens)
    printdbg (retval)

    return retval

class Database:

    place_holder = "?"

    def __init__ (self, database):
        self.database = database

    def connect (self):
        raise NotImplementedError

class SqliteDatabase (Database):

    def __init__ (self, database):
        Database.__init__ (self, database)

    def connect (self):
        import pysqlite2.dbapi2 as db

        return db.connect (self.database)

    def create_tables (self, cursor):
        import pysqlite2.dbapi2

        try:
            cursor.execute ('''CREATE TABLE files (
                            id integer primary key,
                            path varchar
                            )''')
            cursor.execute ('''CREATE TABLE authors (
                            id integer primary key,
                            name varchar
                            )''')
            cursor.execute ('''CREATE TABLE revisions (
                            id integer primary key,
                            revision varchar
                            )''')
            cursor.execute ('''CREATE TABLE blame (
                            id integer primary key,
                            file_id integer,
                            revision_id integer,
                            author_id integer,
                            line integer,
                            date datetime,
                            orig_path varchar
                            )''')
        except pysqlite2.dbapi2.OperationalError:
            raise TableAlreadyExists
        except:
            raise

class MysqlDatabase (Database):

    place_holder = "%s"

    def __init__ (self, database, username, password, hostname):
        Database.__init__ (self, database)

        self.username = username
        self.password = password
        self.hostname = hostname

        self.db = None

    def connect (self):
        import MySQLdb
        import _mysql_exceptions

        try:
            if self.password is not None:
                return MySQLdb.connect (self.hostname, self.username, self.password, self.database, charset = 'utf8')
            else:
                return MySQLdb.connect (self.hostname, self.username, db = self.database, charset = 'utf8')
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1049:
                raise DatabaseNotFound
            elif e.args[0] == 1045:
                raise AccessDenied (str (e))
            else:
                raise DatabaseException (str (e))
        except:
            raise

    def create_tables (self, cursor):
        import _mysql_exceptions

        try:
            cursor.execute ('''CREATE TABLE files (
                            id INT primary key,
                            path varchar(255)
                            ) CHARACTER SET=utf8''')
            cursor.execute ('''CREATE TABLE authors (
                            id INT primary key,
                            name varchar(255)
                            ) CHARACTER SET=utf8''')
            cursor.execute ('''CREATE TABLE revisions (
                            id INT primary key,
                            revision mediumtext
                            ) CHARACTER SET=utf8''')
            cursor.execute ('''CREATE TABLE blame (
                            id INT primary key,
                            file_id INT,
                            revision_id INT,
                            author_id INT,
                            line INT,
                            date datetime,
                            orig_path varchar(255),
                            FOREIGN KEY (file_id) REFERENCES files(id),
                            FOREIGN KEY (revision_id) REFERENCES revisions(id),
                            FOREIGN KEY (author_id) REFERENCES authors(id)
                            ) CHARACTER SET=utf8''')
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1050:
                raise TableAlreadyExists
            else:
                raise DatabaseException (str (e))
        except:
            raise

# TODO
# class CAPostgresDatabase (CADatabase):

def create_database (driver, database, username = None, password = None, hostname = None):
    if driver == 'sqlite':
        db = SqliteDatabase (database)
        return db
    elif driver == 'mysql':
        db = MysqlDatabase (database, username, password, hostname)
    elif driver == 'postgres':
        # TODO
        raise DatabaseDriverNotSupported
    else:
        raise DatabaseDriverNotSupported

    # Try to connect to database
    try:
        db.connect ().close ()
        return db
    except AccessDenied, e:
        if password is None:
            import sys, getpass

            # FIXME: catch KeyboardInterrupt exception
            # FIXME: it only works on UNIX (/dev/tty),
            #  not sure whether it's bug or a feature, though
            oldout, oldin = sys.stdout, sys.stdin
            sys.stdin = sys.stdout = open ('/dev/tty', 'r+')
            password = getpass.getpass ()
            sys.stdout, sys.stdin = oldout, oldin

            return create_database (driver, database, username, password, hostname)
        raise e

    return db

class DBOutputDevice (OutputDevice):

    def __init__ (self):
        config = Config ()
        self.cnn = self.cursor = None

        try:
            self.db = create_database (config.db_driver,
                                       config.db_database,
                                       config.db_user,
                                       config.db_password,
                                       config.db_hostname)
        except AccessDenied, e:
            raise OutputDeviceError ("Error creating database: %s" % e.message)
        except DatabaseNotFound:
            raise OutputDeviceError ("Database %s doesn't exist. It must be created before running guilty" % config.db_database)
        except DatabaseDriverNotSupported:
            raise OutputDeviceError ("Database driver %s is not supported by guilty" % config.db_driver)
        except Exception, e:
            raise OutputDeviceError ("Database error: %s" % (str(e)))

    def begin (self, uri):
        self.cnn = self.db.connect ()
        self.cursor = self.cnn.cursor ()
        try:
            self.db.create_tables (self.cursor)
            self.cnn.commit ()
        except TableAlreadyExists:
            raise OutputDeviceError ("Database is not empty, guilty must be run on an empty database")
        except DatabaseException, e:
            raise OutputDeviceError ("Database error: %s" % (str(e)))

        self.authors = {}
        self.revisions = {}

    def end (self):
        try:
            if self.cnn:
                self.cnn.close ()
            if self.cursor:
                self.cursor.close ()
        except:
            pass
        self.cnn = self.cursor = None
        del self.revisions
        del self.authors

    def __insert_object (self, obj):
        query, args = obj.build_insert ()
        self.cursor.execute (statement (query, self.db.place_holder), args)

        return obj

    def __get_revision_id (self, revision):
        try:
            return self.revisions[revision]
        except KeyError:
            self.revisions[revision] = self.__insert_object (DBRevision (revision)).id
            return self.revisions[revision]

    def __get_author_id (self, author):
        try:
            return self.authors[author]
        except KeyError:
            self.authors[author] = self.__insert_object (DBAuthor (author)).id
            return self.authors[author]

    def start_file (self, filename):
        self.file_id = self.__insert_object (DBFile (filename)).id

    def line (self, line):
        db_line = DBLine (line.line, line.date,line.file)
        db_line.file_id = self.file_id
        db_line.revision_id = self.__get_revision_id (line.rev)
        db_line.author_id = self.__get_author_id (line.author)

        self.__insert_object (db_line)

    def end_file (self):
        self.cnn.commit ()
        self.file_id = -1

register_output_device ('db', DBOutputDevice)
