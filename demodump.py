'''
Created on Jul 11, 2014

@author: Chris
'''
from demofile import DemoFile, DemoMessage
from netmessages_public_pb2 import *
from cstrike15_usermessages_public_pb2 import *
import struct


    
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
            if t.msg_type == 6 and not item.textallchat and not playerteam[item.ent_idx] == playerteam[2]:
                #print item.ent_idx
                #print item.chat
                #print item.msg_name + ":"
                for i in range(1, len(item.params) - 2):
                    print "[" + str(item.ent_idx) + "] " + item.params[0] + ": " + item.params[i]
                #print "------"
                #print item.textallchat
            #elif t.msg_type == 5:
                #print t.text
            #print dir(item)

GAMEEVENT_TYPES = {2:"val_string",
                   3:"val_float",
                   4:"val_long",
                   5:"val_short",
                   6:"val_byte",
                   7:"val_bool",
                   8:"val_uint64",
                   9:"val_wstring"}
            
class GameEvent(object):
    def __init__(self, raw, descriptor):
        self.raw = raw
        self.descriptor = descriptor
        
        #convert the val_ stuff to actual property names
        index = 0
        for keyname in self.descriptor[3]:
            setattr(self, keyname[1], getattr(self.raw.keys[index], GAMEEVENT_TYPES[keyname[0] + 1]))
            index += 1
       
class DemoDump(object):
    '''
    Dumps a CSGO demo
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.NET_MSG = {
                        net_NOP: [],
                        net_Disconnect: [],
                        net_File: [],
                        net_Tick: [],
                        net_StringCmd: [],
                        net_SetConVar: [],
                        net_SignonState: [],
                        svc_ServerInfo: [],
                        svc_SendTable: [],
                        svc_ClassInfo: [],
                        svc_SetPause: [],
                        svc_CreateStringTable: [],
                        svc_UpdateStringTable: [],
                        svc_VoiceInit: [],
                        svc_VoiceData: [],
                        svc_Print: [],
                        svc_Sounds: [],
                        svc_SetView: [],
                        svc_FixAngle: [],
                        svc_CrosshairAngle: [],
                        svc_BSPDecal: [],
                        svc_UserMessage: [],
                        svc_GameEvent: [],
                        svc_PacketEntities: [],
                        svc_TempEntities: [],
                        svc_Prefetch: [],
                        svc_Menu: [],
                        svc_GameEventList: [],
                        svc_GetCvarValue: []
                        }
        self.USER_MESSAGES = {}
        self.GAME_EVENTS = {}
        
        self.descriptors = {}
        self.register_on_netmsg(svc_GameEvent, self.handle_gameevent)
        self.register_on_netmsg(svc_GameEventList, self.handle_gameeventlist)
        self.register_on_netmsg(svc_ServerInfo, self.server_info_update)
        
    def open(self, filename):
        self.demofile = DemoFile()
        return self.demofile.open(filename)
    
    def server_info_update(self, cmd, data):
        info = CSVCMsg_ServerInfo()
        info.ParseFromString(data)
        self.server_info = info
    
    def register_on_netmsg(self, msg, callback):
        if msg not in self.NET_MSG:
            raise "Net message not found"
        self.NET_MSG[msg].append(callback)
    
    def register_on_gameevent(self, msg, callback):
        '''
        msg = event id
        '''
        if not msg in self.GAME_EVENTS:
            self.GAME_EVENTS[msg] = []
        self.GAME_EVENTS[msg].append(callback)
    
    def register_on_usermessage(self, msg, callback):
        if not msg in self.USER_MESSAGES:
            self.USER_MESSAGES[msg] = []
        self.USER_MESSAGES[msg].append(callback)
    
    def handle_gameeventlist(self, cmd, data):
        gameeventlist = CSVCMsg_GameEventList()
        gameeventlist.ParseFromString(data)
        for desc in gameeventlist.descriptors:
            self.descriptors[desc.eventid] = (desc.eventid, desc.name, desc.keys, [])
            for key in desc.keys:
                self.descriptors[desc.eventid][3].append([key.type, key.name])
    
    def handle_gameevent(self, cmd, data):
        '''
        handles the game events and fires the callback
        '''
        gameevent = CSVCMsg_GameEvent()
        gameevent.ParseFromString(data)
        if gameevent.eventid in self.GAME_EVENTS:
            event = GameEvent(gameevent, self.descriptors[gameevent.eventid])
            for callback in self.GAME_EVENTS[event.raw.eventid]:
                callback(event)
            
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
                for callback in self.NET_MSG[cmd]:
                    callback(cmd, data);
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
            