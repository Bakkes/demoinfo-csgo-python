'''
Created on Jul 11, 2014

@author: Chris
'''
from demoinfocsgo.demofile import DemoFile, DemoMessage
from demoinfocsgo.proto.netmessages_pb2 import *
from demoinfocsgo.proto.cstrike15_usermessages_pb2 import *
import struct

_GAMEEVENT_TYPES = {2:"val_string",
                   3:"val_float",
                   4:"val_long",
                   5:"val_short",
                   6:"val_byte",
                   7:"val_bool",
                   8:"val_uint64",
                   9:"val_wstring"}
 
class GameEvent(object):
    '''
    Object that is passed when a game event is fired, for all game events, see: data/game_events.txt
    '''
    
    def __init__(self, raw, descriptor, name):
        self.raw = raw
        self.descriptor = descriptor
        self.name = name
        # convert the val_ stuff to actual property names
        index = 0
        for keyname in self.descriptor[3]:
            setattr(self, keyname[1], getattr(self.raw.keys[index], _GAMEEVENT_TYPES[keyname[0] + 1]))
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
        self.current_tick = 0
        self.descriptors = {}
        self.register_on_netmsg(svc_GameEvent, self._handle_gameevent)
        self.register_on_netmsg(svc_GameEventList, self._handle_gameeventlist)
        self.register_on_netmsg(svc_UserMessage, self._handle_usermessage)
        self.register_on_netmsg(svc_ServerInfo, self._server_info_update)
        self.register_on_netmsg(svc_CreateStringTable, self._server_create_stringtable)
        self.register_on_netmsg(svc_SendTable, self._send_table)
        self.register_on_netmsg(svc_UpdateStringTable, self._update_stringtable)
        self.register_on_netmsg(svc_ClassInfo, self._handle_classinfo)
        self.register_on_netmsg(net_Tick, self._handle_tick)
        
    def open(self, filename):
        '''
        Opens the demo file.
        '''
        self.demofile = DemoFile()
        return self.demofile.open(filename)
    
    
    def register_on_netmsg(self, msg, callback):
        '''
        Will register a callback to call when the given netmessage is received.
        Will throw an exception if the netmessage doesn't exist. For all netmessages see: netmessages_public.proto SVC_Messages
        '''
        if msg not in self.NET_MSG:
            raise "Net message not found"
        self.NET_MSG[msg].append(callback)
    
    def register_on_gameevent(self, msg, callback):
        '''
        Will register a callback to call when the given game event is called.
        Can give ID or name, SHOULD USE NAME, BECAUSE IDS CHANGE (?)
        Game events can be found in data/game_events.txt
        '''
        if msg not in self.GAME_EVENTS:
            self.GAME_EVENTS[msg] = []
        self.GAME_EVENTS[msg].append(callback)
    
    def register_on_usermessage(self, msg, callback):
        '''
        Not yet implemented.
        '''
        if not msg in self.USER_MESSAGES:
            self.USER_MESSAGES[msg] = []
        self.USER_MESSAGES[msg].append(callback)
    
    def dump(self):
        '''
        Will start analyzing the demo and executing the necessary game events
        '''
        finished = False
        while not finished:
            cmd, tick, playerslot = self.demofile.read_cmd_header()
            # print "%i - %i - % i " % (cmd, tick, playerslot)
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
                self._handle_demo_packet()
    
    def _handle_usermessage(self, cmd, data):
        umsg = CSVCMsg_UserMessage()
        umsg.ParseFromString(data)
        name = ECstrike15UserMessages.Name(umsg.msg_type)
        callback_name = name.replace("CS_UM_", "")
        if callback_name in self.USER_MESSAGES:
            name = name.replace("CS_UM_", "CCSUsrMsg_")
            item = eval(name)()
            item.ParseFromString(umsg.msg_data)
            for callback in self.USER_MESSAGES[callback_name]:
                callback(item)
                
    def _handle_tick(self, cmd, data):
        tickinfo = CNETMsg_Tick()
        tickinfo.ParseFromString(data)
        self.current_tick = tickinfo.tick
    
    def _server_info_update(self, cmd, data):
        info = CSVCMsg_ServerInfo()
        info.ParseFromString(data)
        self.server_info = info
    
    def _handle_gameeventlist(self, cmd, data):
        '''
        Parses the list of given game events by the server
        '''
        gameeventlist = CSVCMsg_GameEventList()
        gameeventlist.ParseFromString(data)
        for desc in gameeventlist.descriptors:
            self.descriptors[desc.eventid] = (desc.eventid, desc.name, desc.keys, [])
            for key in desc.keys:
                self.descriptors[desc.eventid][3].append([key.type, key.name])
    
    def _handle_gameevent(self, cmd, data):
        '''
        handles the game events and fires the callback
        '''
        gameevent = CSVCMsg_GameEvent()
        gameevent.ParseFromString(data)
        name = self.descriptors[gameevent.eventid][1]
        if gameevent.eventid in self.GAME_EVENTS :
            event = GameEvent(gameevent, self.descriptors[gameevent.eventid], name)
            for callback in self.GAME_EVENTS[event.raw.eventid]:
                callback(event)
                
        
        if name in self.GAME_EVENTS:
            event = GameEvent(gameevent, self.descriptors[gameevent.eventid], name)
            for callback in self.GAME_EVENTS[name]:
                callback(event)
         
    stringtable_data = {}
    def _server_create_stringtable(self, cmd, data):
        '''
        Creates a string table from the given data.
        TO BE IMPLEMENTED
        '''
        table = CSVCMsg_CreateStringTable()
        # table_data = CSVCMsg_SendTable()
        table.ParseFromString(data)
        if table.name != "userinfo":
            return
        # table_data.ParseFromString(table.string_data)
        self.stringtable_data[table.name] = {'entries': table.num_entries,
                                             'user_data_fixed_size': table.user_data_fixed_size,
                                             'user_data_size': table.user_data_size,
                                             'user_data_size_bits': table.user_data_size_bits,
                                             'flags': table.flags,
                                             # 'data': table_data
                                             }
        '''
                int *pStringIndex = (int *)fieldInfo.pField;
        int nLen = pRestore->ReadInt();
        char *pTemp = (char *)stackalloc( nLen );
        pRestore->ReadString( pTemp, nLen, nLen );
        *pStringIndex = m_pStringTable->AddString( CBaseEntity::IsServer(), pTemp );
        '''
        
    def _update_stringtable(self, cmd, data):
        '''
        Updates a stringtable with the given data
        TO BE IMPLEMENTED
        '''
        update = CSVCMsg_UpdateStringTable()
        update.ParseFromString(data)
        
    def _send_table(self, cmd, data):
        table = CSVCMsg_SendTable()
        table.ParseFromString(data)
        print "%s: is end: %r, needs_decoder: %r" % (table.net_table_name, table.is_end, table.needs_decoder)
        for prop in table.props:
            print "Name: %s type: %i" % (prop.var_name, prop.type)
        print "-------------------------------"
        
    def _handle_classinfo(self, cmd, data):
        info = CSVCMsg_ClassInfo()
        info.ParseFromString(data)
        #print "CLASS INFO COUNT: %s, CREATE ON CLIENT: %r" % (len(info.classes), info.create_on_client)
        #for c in info.classes:
        #    print "%i: %s, %s" % (c.class_id, c.data_table_name, c.class_name)
                
    def _handle_demo_packet(self):
        info = self.demofile.read_cmd_info()
        self.demofile.read_sequence_info()  # ignore result
        length, buf = self.demofile.read_raw_data()
        
        if length > 0:
            self._dump_packet(buf, length)
         
            
    def _dump_packet(self, buf, length):
        index = 0
        while index < length:
            cmd, index = self.__read_int32(buf, index)
            size, index = self.__read_int32(buf, index)
            data = buf[index:index + size]
            if cmd in self.NET_MSG:
                for callback in self.NET_MSG[cmd]:
                    
                    callback(cmd, data);
                    
            index = index + size
        
    def __read_int32(self, buf, index):
        '''
        Reads an int32 from a binary buffer.
        '''
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
            