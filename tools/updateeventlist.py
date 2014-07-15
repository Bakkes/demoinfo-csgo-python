'''
Creates a formatted list of game events

Created on Jul 12, 2014

@author: Chris
'''
from demoinfocsgo.demodump import DemoDump
from demoinfocsgo.proto.netmessages_public_pb2 import svc_GameEventList, CSVCMsg_GameEventList
import sys
import json

events = {}
_GAMEEVENT_TYPES = {2:"string",
                   3:"float",
                   4:"long",
                   5:"short",
                   6:"byte",
                   7:"bool",
                   8:"uint64",
                   9:"wstring"}

def on_list_received(msg, data):
    t = CSVCMsg_GameEventList()
    t.ParseFromString(data)

    for desc in t.descriptors:
        events[desc.name] = {
                             "ID": desc.eventid,
                             "name": desc.name,
                             "params": {}
                                }
        for key in desc.keys:
            events[desc.name]["params"][key.name] = _GAMEEVENT_TYPES[key.type + 1]

if __name__ == '__main__':
    demo = DemoDump()
    filename = sys.argv[1]
    
    if len(sys.argv) <= 1:
        print "updateeventlist.py demofile.dem"
        sys.exit()        
        
    if demo.open(filename):
        print "Beginning parsing"
        demo.register_on_netmsg(svc_GameEventList, on_list_received)
        demo.dump()
        json_data = json.dumps(events, indent=4)
        print json_data
        f = open("../data/game_events.txt", "w")
        f.write(json_data)
        print "Saved to file data/game_events.txt"