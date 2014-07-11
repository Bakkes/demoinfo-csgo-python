'''
Created on Jul 11, 2014

@author: Chris
'''
from demofile import DemoFile, DemoMessage


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
        return self.demofile.open(filename)
        '''
        '''
    
    def dump(self):
        finished = False
        print "dumping"
        while not finished:
            cmd, tick, playerslot = self.demofile.read_cmd_header()
            print "%i - %i - % i " % (cmd, tick, playerslot)
            if cmd == DemoMessage.SYNCTICK:
                continue
            elif cmd == DemoMessage.STOP:
                finished = True
                break
            elif cmd == DemoMessage.CONSOLECMD:
                self.demofile.read_raw_data(0)
            elif cmd == DemoMessage.DATATABLES:
                self.demofile.read_raw_data(0)
            elif cmd == DemoMessage.STRINGTABLES:
                self.demofile.read_raw_data(0)
            elif cmd == DemoMessage.CONSOLECMD:
                dummy = 0
                self.demofile.read_raw_data(dummy)
            elif cmd == DemoMessage.SIGNON or cmd == DemoMessage.PACKET:
                print "Packet found"
                self.handle_demo_packet()
                
    def handle_demo_packet(self):
        info = self.demofile.read_cmd_info()
        self.demofile.read_sequence_info()#ignore result
        length = self.demofile.read_raw_data()
        print "length: " + str(length)
        if length > 0:
            self.dump_packet(length)
            
    def dump_packet(self, length):
        index = 0
        while index < length:
            cmd = self.__read_int32()
            size = self.__read_int32()
            #read data
            self.demofile.file.read(size)
            
    def __read_int32(self):
        b = 0
        count = 0
        result = 0
        
        cont = True
        while cont:
            if count == 5:
                return result
            b = self.demofile.file.read(1)
            result |= (b & 0x7F) << (7 * count)
            count = count + 1
            cont = b & 0x80
        return result
            