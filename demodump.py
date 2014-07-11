'''
Created on Jul 11, 2014

@author: Chris
'''
from demofile import DemoFile
class DemoDump(object):
    '''
    Dumps a CSGO demo
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def open(self, filename):
        self.demofile = DemoFile()
        self.demofile.open(filename)
        '''
        '''