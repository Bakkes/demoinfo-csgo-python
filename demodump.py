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
   
import bitstring
class StringTable(object):
    def __init__(self):
        pass
    
    def decode(self, data):
        stream = bitstring.BitStream(bytes=data)
        flag = stream.read('bin:1') == '0'
        index = -1
        
        while True:
            print stream.read('bin:1')
            return
            if stream.read('bin:1'):
                index += 1
            else:
                index = stream
        print flag
        #while True:
            
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
        self.register_on_netmsg(svc_CreateStringTable, self.server_create_stringtable)
        self.register_on_netmsg(svc_SendTable, self.send_table)
        self.register_on_netmsg(svc_UpdateStringTable, self.update_stringtable)
        self.register_on_netmsg(svc_ClassInfo, self.handle_classinfo)
        
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
         
    stringtable_data = {}
    def server_create_stringtable(self, cmd, data):
        table = CSVCMsg_CreateStringTable()
        #table_data = CSVCMsg_SendTable()
        table.ParseFromString(data)
        if table.name != "userinfo":
            return
        #table_data.ParseFromString(table.string_data)
        self.stringtable_data[table.name] = {'entries': table.num_entries,
                                             'user_data_fixed_size': table.user_data_fixed_size,
                                             'user_data_size': table.user_data_size,
                                             'user_data_size_bits': table.user_data_size_bits,
                                             'flags': table.flags,
                                             #'data': table_data
                                             }
        '''
                int *pStringIndex = (int *)fieldInfo.pField;
        int nLen = pRestore->ReadInt();
        char *pTemp = (char *)stackalloc( nLen );
        pRestore->ReadString( pTemp, nLen, nLen );
        *pStringIndex = m_pStringTable->AddString( CBaseEntity::IsServer(), pTemp );
        '''
        
    inx = 0
    def update_stringtable(self, cmd, data):
        update = CSVCMsg_UpdateStringTable()
        update.ParseFromString(data)
        #print "Table %i updated, changed: %i" % (update.table_id, update.num_changed_entries)
        #print update.string_data
        self.inx += 1
        
    def send_table(self, cmd, data):
        table = CSVCMsg_SendTable()
        table.ParseFromString(data)
        print "%s: is end: %r, needs_decoder: %r" % (table.net_table_name, table.is_end, table.needs_decoder)
        for prop in table.props:
            print "Name: %s type: %i" % (prop.var_name, prop.type)
        print "-------------------------------"
        
    def handle_classinfo(self, cmd, data):
        info = CSVCMsg_ClassInfo()
        info.ParseFromString(data)
        print "CLASS INFO COUNT: %s, CREATE ON CLIENT: %r" % (len(info.classes), info.create_on_client)
        for c in info.classes:
            print "%i: %s, %s" % (c.class_id, c.data_table_name, c.class_name)
            
    def dump(self):
        finished = False
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
                self.handle_demo_packet()
                
    def handle_demo_packet(self):
        info = self.demofile.read_cmd_info()
        self.demofile.read_sequence_info()#ignore result
        length, buf = self.demofile.read_raw_data()
        
        if length > 0:
            self.dump_packet(buf, length)
         
            
    def dump_packet(self, buf, length):
        index = 0
        while index < length:
            cmd, index = self.__read_int32(buf, index)
            size, index = self.__read_int32(buf, index)
            data = buf[index:index+size]
            if cmd in self.NET_MSG:
                for callback in self.NET_MSG[cmd]:
                    callback(cmd, data);
                    
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
            