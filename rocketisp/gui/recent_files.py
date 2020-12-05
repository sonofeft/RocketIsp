#!/usr/bin/env python
# -*- coding: ascii -*-

import os
import sys
from rocketisp.gui.config_file import ConfigInterface

USER_HOME_DIR = os.path.dirname( os.path.expanduser('~/') )

class RecentFiles( object ):
    MaxRecentFiles = 99
    
    def __init__(self, config_file_prefix='RocketIspGUI'):
        
        self.file_name = os.path.join( USER_HOME_DIR, '%s.cfg'%config_file_prefix )
        self.config_obj = ConfigInterface( config_filename=self.file_name, 
                                            sectionL=['RecentFiles'] )
        
        self.recent_fileL = []
        self.recent_metadataL = [] # any meta data that file might have.
        
        D = self.config_obj.get_dictionary()['RecentFiles']
        
        self.last_dir = D.get('last_dir',USER_HOME_DIR)
        
        for i in range(RecentFiles.MaxRecentFiles):
            fname = D.get( 'file_%i'%(i+1,), '')
            if fname:
                self.recent_fileL.append( fname )
                
                # if there's any metadata, grab it also.
                meta = D.get( 'meta_%i'%(i+1,), '')
                self.recent_metadataL.append( meta )# add to list even if ''
            
    
    def get_most_recent_file(self):
        if self.recent_fileL:
            return self.recent_fileL[0], self.recent_metadataL[0]
    
    def __len__(self):
        return len( self.recent_fileL )
    
    def get_full_path_list(self):
        
        return self.recent_fileL[:]  # return a copy
    
    def update(self, fname, metadata=''):
        
        fname = fname.replace('/','\\')
        
        head,tail = os.path.split( fname )
        
        self.config_obj['RecentFiles','last_dir'] = head
        
        self.last_dir = head
        
        while fname in self.recent_fileL:
            try:
                i = self.recent_fileL.index( fname )
                del self.recent_fileL[ i ]
                del self.recent_metadataL[ i ]
            except ValueError:
                break
        
        self.recent_fileL.insert(0, fname)
        self.recent_metadataL.insert(0, metadata)
                
        for i in range( RecentFiles.MaxRecentFiles ):
            if i < len( self.recent_fileL ):
                self.config_obj['RecentFiles','file_%i'%(i+1,)] = self.recent_fileL[i]
                self.config_obj['RecentFiles','meta_%i'%(i+1,)] = self.recent_metadataL[i]
            else:
                self.config_obj['RecentFiles','file_%i'%(i+1,)] = ''
                self.config_obj['RecentFiles','meta_%i'%(i+1,)] = ''
                
        self.config_obj.save_file()
        
    def save(self):
        self.config_obj.save_file()
        
        
    def set_dir(self, filePath):
        self.config_obj['RecentFiles','last_dir'] = filePath
        self.config_obj.save_file()
    
    def get_dir(self):
        if self.config_obj.has_option('RecentFiles', 'last_dir'):
            filePath = self.config_obj['RecentFiles', 'last_dir']
        else:
            filePath = USER_HOME_DIR # os.getcwd()
        return filePath
    
    def chdir(self):
        filePath = self.get_dir()
        print( "Changing Directory To:",filePath )
        os.chdir( filePath )
 
if __name__ == "__main__":
     
    RF = RecentFiles()
    
    print( RF.config_obj.get_dictionary() )
    print()
    print( RF.recent_fileL )
     