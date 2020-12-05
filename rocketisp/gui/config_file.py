#!/usr/bin/env python
# -*- coding: ascii -*-

r"""
ConfigFile wraps a configparser file as an in-memory container with a few
more options.

such as:
    mycfg['BadNews','IQ'] = 'very low'
    x = mycfg['BadNews','IQ']
    del mycfg['BadNews','IQ']
    mycfg.save_file()
    myDict = mycfg.get_dictionary()
           
Save to file can be triggered by a "has_changes" flag.


ConfigFile
Copyright (C) 2015  Charlie Taylor

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

-----------------------

"""

# for multi-file projects see LICENSE file for authorship info
# for single file projects, insert following information
__author__ = 'Charlie Taylor'
__copyright__ = 'Copyright (c) 2013 Charlie Taylor'
__license__ = 'GPL-3'
__version__ = '0.1.1' #Versioning: http://www.python.org/dev/peps/pep-0386/
__email__ = "cet@appliedpython.com"
__status__ = "Development" # "Prototype", "Development", or "Production"

#
# import statements here. (built-in first, then 3rd party, then yours)
import sys
import os
import configparser
from configparser import NoOptionError, NoSectionError

class ConfigInterface(object):
    """ConfigFile wraps a configparser file as an in-memory container
    """

    def __init__(self, config_filename='myconfig.cfg', sectionL=None):
        """Inits ConfigInterface a ConfigParser and a config file name.
        
           :param config_filename: name of config file (data files also in config format)
           :param sectionL: a list of section headings in config file
           
           :type config_filename: string
           :type sectionL: list of strings
        """
        self.has_changes = False # If True, then a save_file should be done
        self.state_id_number = 0 # is incremented each time a change takes place
        
        self.config_filename= os.path.abspath( config_filename )
        
        if config_filename.lower().endswith('.cfg'):
            print( 'Config File:', self.config_filename )
        else:
            print( 'Data File:', self.config_filename )
            
        #self.config = configparser.SafeConfigParser()
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str
                
        if os.path.isfile(self.config_filename):
            self.config.read(self.config_filename)
            self.config_files_first_open = False
        else:
            self.config_files_first_open = True # 1st time accessing (needs a save_file to create)
            
        if sectionL:
            for section in sectionL:
                if not self.config.has_section( section ):
                    self.config.add_section(section)
                    self.has_changes = True
                    self.state_id_number += 1
    
    def get_sectionL(self):
        """Return a list of all sections in config file"""
        return self.config.sections()
        
    def get_optionL(self, section):
        """Return a list of options for section  in config file"""
        return self.config.options(section)
        
    def get_dictionary(self):
        """Make a dictionary representation of config file"""
        D = {} # build from empty dictionary
        for section in self.config.sections():
            sectD = {} # section dictionary
            for option in self.config.options(section):
                sectD[option] = self.config.get(section, option)
            D[section] = sectD
            
        return D
                
    
    def set(self, section, option, value):
        """Calls configparser set method and sets self.has_changes=True"""
        if not self.config.has_section( section ):
            self.config.add_section(section)
        
        self.config.set(section, option, value)
        self.has_changes = True
        self.state_id_number += 1
    
    def has_section(self, section):
        """Calls configparser has_section method"""
        return self.config.has_section(section)
    
    def has_option(self, section, option):
        """Calls configparser has_section method"""
        return self.config.has_option(section, option)
    
    def save_file(self):
        """Saves self.config to self.config_filename
           Also sets self.has_changes=False
        """
        with open(self.config_filename, 'w') as configfile:
            self.config.write( configfile )
        
        # if has_changes is reset to True, then another save_file should be done
        self.has_changes = False
        
    def delete_file(self):
        """Deletes self.config_filename"""
        if os.path.isfile( self.config_filename ):
            os.remove( self.config_filename )

    def __getitem__(self, key_tup):
        """Allows data access such as:
           mycfg['BadNews','IQ']
        """
        if len(key_tup)==2:
            section, option = key_tup
            try:
                return self.config.get(section, option)
            except (NoOptionError, NoSectionError):
                return None
            
    def __setitem__(self, key_tup, value):
        """Allows assignments such as:
           mycfg['BadNews','IQ'] = 'very low'
           (changes self.has_changes to True as a side-effect)
        """
        if len(key_tup)==2:
            section, option = key_tup
            self.set(section, option, value)
            
    def __delitem__(self, key_tup):
        """Allows removal of item as:
           del mycfg['BadNews','IQ']
           (changes self.has_changes to True as a side-effect)
        """
        if len(key_tup)==2:
            section, option = key_tup
            try:
                self.state_id_number += 1
                self.config.remove_option(section, option)
                self.has_changes = True
            except (NoOptionError, NoSectionError):
                pass # if not deletable, don't worry about it


if __name__ == '__main__':
    C = ConfigInterface()
    #C.save_file()
