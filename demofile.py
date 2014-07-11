'''
Created on Jul 11, 2014

@author: Chris
'''
import os

import cstrike15_usermessages_public_pb2
import netmessages_public_pb2

import struct

class DemoHeader(object):
    def __init__(self, demofile, demoprotocol, networkprotocol,
                 servername, clientname, mapname, gamedirectory,
                 playback_time, playback_ticks, playback_frames,
                 signonlength):
        self.demofile = demofile.rstrip('\0')
        self.demoprotocol = demoprotocol
        self.networkprotocol =  networkprotocol
        self.servername = servername.rstrip('\0')
        self.clientname = clientname.rstrip('\0')
        self.mapname = mapname.rstrip('\0')
        self.gamedirectory = gamedirectory.rstrip('\0')
        self.playback_time = playback_time
        self.playback_ticks = playback_ticks
        self.playback_frames = playback_frames
        self.signonlength = signonlength

class DemoFile(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.demoheader = None
        
    def open(self, filename):
        self.file = open(filename, "r")
        if(self.file):
            print "Succesfully opened file"
            self.file.seek(0, os.SEEK_END) #get file size
            length = self.file.tell()
            self.file.seek(0, os.SEEK_SET) #get back to beginning
        
            #parse header
            struct_fmt = "=8sii260s260s260s260sfiii"
            struct_len = struct.calcsize(struct_fmt)
            struct_unpack = struct.Struct(struct_fmt)
            self.file.seek(0, os.SEEK_SET)
            data = self.file.read(struct_len)
            read = struct_unpack.unpack_from(data, 0)
            self.demoheader = DemoHeader(*list(read))
            
            