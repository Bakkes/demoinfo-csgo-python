'''
Created on Jul 15, 2014

@author: Chris
'''

from demodump import DemoDump
from netmessages_public_pb2 import *
import json
_DUMPED_TYPES = {
                    net_NOP: ("CNETMsg_NOP"),
                    net_Disconnect: ("CNETMsg_Disconnect"),
                    net_File: ("CNETMsg_File"),
                    net_Tick: ("CNETMsg_Tick"),
                    net_StringCmd: ("CNETMsg_StringCmd"),
                    net_SetConVar: ("CNETMsg_SetConVar"),
                    net_SignonState: ("CNETMsg_SignonState"),
                    svc_ServerInfo: ("CSVCMsg_ServerInfo"),
                    svc_SendTable: ("CSVCMsg_SendTable"),
                    svc_ClassInfo: ("CSVCMsg_ClassInfo"),
                    svc_SetPause: ("CSVCMsg_SetPause"),
                    svc_CreateStringTable: ("CSVCMsg_CreateStringTable"),
                    svc_UpdateStringTable: ("CSVCMsg_UpdateStringTable"),
                    svc_VoiceInit: ("CSVCMsg_VoiceInit"),
                    svc_VoiceData: ("CSVCMsg_VoiceData"),
                    svc_Print: ("CSVCMsg_Print"),
                    svc_Sounds: ("CSVCMsg_Sounds"),
                    svc_SetView: ("CSVCMsg_SetView"),
                    svc_FixAngle: ("CSVCMsg_FixAngle"),
                    svc_CrosshairAngle: ("CSVCMsg_CrosshairAngle"),
                    svc_BSPDecal: ("CSVCMsg_BSPDecal"),
                    svc_UserMessage: ("CSVCMsg_UserMessage"),
                    svc_GameEvent: ("CSVCMsg_GameEvent"),
                    svc_PacketEntities: ("CSVCMsg_PacketEntities"),
                    svc_TempEntities: ("CSVCMsg_TempEntities"),
                    svc_Prefetch: ("CSVCMsg_Prefetch"),
                    svc_Menu: ("CSVCMsg_Menu"),
                    svc_GameEventList: ("CSVCMsg_GameEventList"),
                    svc_GetCvarValue: ("CSVCMsg_GetCvarValue")
                 }

from protojson.pbliteserializer import PbLiteSerializer
from protojson.error import PbDecodeError
import simplejson
class JSONDumper(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        if self.demo.open(filename):
            for t in _DUMPED_TYPES:
                self.demo.register_on_netmsg(t, self.on_netmsg)
            
            self.demo.dump()    
    
    def on_netmsg(self, id, data):
        inst = eval(_DUMPED_TYPES[id])()
        inst.ParseFromString(data)
        
        name = _DUMPED_TYPES[id].replace("CNETMsg", "net").replace("CSVCMsg", "svc")
        name = "%s (%i)" % (name, id)
        serializer = PbLiteSerializer()
        dict = {name: serializer.serialize(inst)}
        print dict
        
        #json.dumps(vars(data), skipkeys=4)
        
if __name__ == '__main__':
    d = JSONDumper("gotv.dem")
    pass