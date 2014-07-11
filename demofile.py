'''
Created on Jul 11, 2014

@author: Chris
'''
import os

import cstrike15_usermessages_public_pb2
import netmessages_public_pb2

import struct

SUPPORTED_PROTOCOL = 4

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

class DemoCMDInfo(object):
    '''
    '''

class DemoMessage:
    SIGNON = 1
    PACKET = 2
    SYNCTICK = 3
    CONSOLECMD = 4
    USERCMD = 5
    DATATABLES = 6
    STOP = 7
    CUSTOMDATA = 8
    STRINGTABLES = 9
    LASTCMD = STRINGTABLES

class DemoFile(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.demoheader = None
        self.offset = 0
        
    def open(self, filename):
        self.file = open(filename, "rb")
        if self.file:
            
            self.file.seek(0, os.SEEK_END) #get file size
            self.length = self.file.tell()
            self.file.seek(0, os.SEEK_SET) #get back to beginning
        
            #parse header
            struct_fmt = "@8sii260s260s260s260sfiii"
            struct_len = struct.calcsize(struct_fmt)
            struct_unpack = struct.Struct(struct_fmt)
            data = self.file.read(struct_len)
            read = struct_unpack.unpack_from(data, 0)
            self.offset = struct_len
            self.demoheader = DemoHeader(*list(read))
            
            
            if self.demoheader.demoprotocol != SUPPORTED_PROTOCOL:
                print "This protocol is not supported"
                return False
        else:
            return False
        print "Succesfully opened file"
        return True
    
    def read_cmd_header(self):
        cmd = self.read_struct_from_file("B")
        if cmd <= 0:
            cmd = DemoMessage.STOP
            return cmd, 0, 0
        tick = self.read_struct_from_file("i")
        playerslot = self.read_struct_from_file("B")
        return cmd, tick, playerslot
    
    def read_raw_data(self):
        size = self.read_struct_from_file("@i")
        if size <= 0:
            return 0, None
        
        data = self.file.read(size)
        
        self.offset = self.offset + size
        self.file.seek(self.offset)
        return size, data
        
    
    def read_cmd_info(self):
        fmt = "@iffffffffffffffffffiffffffffffffffffff"#x2 because of splitscreen
        return self.read_struct_from_file(fmt)
        
    def read_struct_from_file(self, fmt):
        self.file.seek(self.offset)
        struct_len = struct.calcsize(fmt)
        struct_unpack = struct.Struct(fmt)
        data = self.file.read(struct_len)
        self.offset = self.offset + struct_len
        self.file.seek(self.offset)
        read = struct_unpack.unpack_from(data, 0)
        return read[0]
    
    def read_sequence_info(self):
        seq_nr_in = self.read_struct_from_file("i")
        seq_nr_out = self.read_struct_from_file("i")
        return seq_nr_in, seq_nr_out