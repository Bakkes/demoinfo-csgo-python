'''
Created on Jul 11, 2014

@author: Chris
'''
from demofile import DemoFile, DemoMessage
from netmessages_public_pb2 import *
from cstrike15_usermessages_public_pb2 import *
import struct
import sys

def ignore(name, data):
    '''
    '''
    ##print "%i ignored" % name
    
def handle(id, data):
    if id == svc_UserMessage:
        t = CSVCMsg_UserMessage()
        t.ParseFromString(data)
        if t.msg_type in ECstrike15UserMessages.values():
            name = ECstrike15UserMessages.Name(t.msg_type)
            name = name.replace("CS_UM_", "CCSUsrMsg_")
            #print "Message type %s | %i" % (name, t.msg_type)
            
            item = eval(name)()
            item.ParseFromString(t.msg_data)
            #if t.msg_type == 6:
                #print item.ent_idx
                #print item.chat
                #print item.msg_name + ":"
                #for i in range(1, len(item.params) - 2):
                #    print item.params[0] + ": " + item.params[i] + " - " + str(item.textallchat)
                #print "------"
                #print item.textallchat
            #elif t.msg_type == 5:
                #print t.text
            #print dir(item)
    elif id == svc_GameEvent:
        t = CSVCMsg_GameEvent()
        t.ParseFromString(data)
    elif id == svc_GameEventList:
        t = CSVCMsg_GameEventList()
        t.ParseFromString(data)
        for desc in t.descriptors:
            print "ID: %i, name: %s" % (desc.eventid, desc.name)
            for key in desc.keys:
                print "Key type: %i, name: %s" % (key.type, key.name)
            

class DemoDump(object):
    '''
    Dumps a CSGO demo
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.NET_MSG = {
                        net_NOP: ignore,
                        net_Disconnect: ignore,
                        net_File: ignore,
                        net_Tick: ignore,
                        net_StringCmd: ignore,
                        net_SetConVar: ignore,
                        net_SignonState: ignore,
                        svc_ServerInfo: ignore,
                        svc_SendTable: ignore,
                        svc_ClassInfo: ignore,
                        svc_SetPause: ignore,
                        svc_CreateStringTable: ignore,
                        svc_UpdateStringTable: ignore,
                        svc_VoiceInit: ignore,
                        svc_VoiceData: ignore,
                        svc_Print: ignore,
                        svc_Sounds: ignore,
                        svc_SetView: ignore,
                        svc_FixAngle: ignore,
                        svc_CrosshairAngle: ignore,
                        svc_BSPDecal: ignore,
                        svc_UserMessage: handle,
                        svc_GameEvent: handle,
                        svc_PacketEntities: ignore,
                        svc_TempEntities: ignore,
                        svc_Prefetch: ignore,
                        svc_Menu: ignore,
                        svc_GameEventList: handle,
                        svc_GetCvarValue: ignore
                        }
        
    def open(self, filename):
        self.demofile = DemoFile()
        return self.demofile.open(filename)
        '''
        '''
    
    def dump(self):
        finished = False
        #print "dumping"
        while not finished:
            cmd, tick, playerslot = self.demofile.read_cmd_header()
            #print "%i - %i - % i " % (cmd, tick, playerslot)
            if cmd == DemoMessage.SYNCTICK:
                continue
            elif cmd == DemoMessage.STOP:
                finished = True
                break
            elif cmd == DemoMessage.CONSOLECMD:
                self.demofile.read_raw_data()
            elif cmd == DemoMessage.DATATABLES:
                self.demofile.read_raw_data()
            elif cmd == DemoMessage.STRINGTABLES:
                self.demofile.read_raw_data()
            elif cmd == DemoMessage.USERCMD:
                self.demofile.read_user_cmd()
            elif cmd == DemoMessage.SIGNON or cmd == DemoMessage.PACKET:
                #print "Packet found"
                self.handle_demo_packet()
                
    def handle_demo_packet(self):
        info = self.demofile.read_cmd_info()
        self.demofile.read_sequence_info()#ignore result
        length, buf = self.demofile.read_raw_data()
        
        #print "length: %i|%i" % (length, len(buf))
        if length > 0:
            self.dump_packet(buf, length)
         
            
    def dump_packet(self, buf, length):
        index = 0
        while index < length:
            cmd, index = self.__read_int32(buf, index)
            size, index = self.__read_int32(buf, index)
            #read data
            data = buf[index:index+size]
            #print cmd
            if cmd in self.NET_MSG:
                self.NET_MSG[cmd](cmd, data)
            #else:
                #print "Unknown command: %i" % cmd
            
            index = index + size
        
    def __read_int32(self, buf, index):
        b = 0
        count = 0
        result = 0
        
        cont = True
        while cont:
            if count == 5:
                return result
            b = struct.unpack_from("B", buf, index)
            b = b[0]
            index = index + 1
            result |= (b & 0x7F) << (7 * count)
            count = count + 1
            cont = b & 0x80
        return result, index
            