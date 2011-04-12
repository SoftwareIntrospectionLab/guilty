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

class ErrorLoadingConfig (Exception):
    '''Error loading configuration options'''

class Config:
    __shared_state = {}

    def __init__ (self, init=None):
        if self.__shared_state and not init:
            self.__dict__ = self.__shared_state
            return

        if init is None:
            import os

            # First look in /etc
            # FIXME /etc is not portable
            config_file = os.path.join ('/etc', 'guilty')
            if os.path.isfile (config_file):
                self.__load_from_file (config_file)
            # Then look at $HOME
            config_file = os.path.join (os.environ.get ('HOME'), '.guilty', 'config')
            if os.path.isfile (config_file):
                self.__load_from_file (config_file)
        else:
            import os

            if os.path.isfile (init):
                self.__shared_state.clear ()
                self.__load_from_file (init)

        self.__dict__ = self.__shared_state

    def update (self, options):
        '''Update current options with the ones provided.
        Existing options are updated with the new ones'''
        self.__shared_state.update (options)

    def add (self, options):
        '''Update current options by adding the ones provided.
        If an option already exists in current dict, the new value
        is ignored'''
        fo = dict ([(opt, options[opt]) for opt in options if opt not in self.__shared_state])
        self.update (fo)

    def __getattr__ (self, attr):
        return self.__dict__[attr]

    def __setattr__ (self, attr, value):
        self.__dict__[attr] = value

    def __str__ (self):
        return "Config %r" % (self.__dict__)

    def __repr__ (self):
        return "Config %r" % (self.__dict__)

    def __load_from_file (self, config_file):
        try:
            from types import ModuleType
            config = ModuleType ('guilty-config')
            f = open (config_file, 'r')
            exec f in config.__dict__
            f.close ()
        except Exception, e:
            raise ErrorLoadingConfig ("Error reading config file %s (%s)" % (config_file, str (e)))

        self.update (dict([(key, config.__dict__[key]) for key in config.__dict__ if not key.startswith ('_')]))
