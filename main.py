'''
Created on Jul 11, 2014

@author: Chris
'''
import sys
from demodump import DemoDump


def flashbang_detonate(data):
    '''
    ID: 151, name: flashbang_detonate
Key type: 4, name: userid
Key type: 4, name: entityid
Key type: 2, name: x
Key type: 2, name: y
Key type: 2, name: z'''
    userid = data.keys[0].val_short
    entityid = data.keys[1].val_short
    x, y, z = data.keys[2].val_float, data.keys[3].val_float, data.keys[4].val_float
    print "%i detonated flashbang (%i) at x:%f, y:%f, z:%f" % (userid, entityid, x, y, z)
    
def player_purchase(data):
    '''
    Key type: 4, name: userid
Key type: 4, name: team
Key type: 1, name: weapon'''

    userid = data.keys[0].val_short
    team = data.keys[1].val_short
    weapon_name = data.keys[2].val_string
    print "%i bought %s" % (userid, weapon_name)
    
    

if __name__ == '__main__':
    demo = DemoDump()
    filename = sys.argv[1]
    
    if len(sys.argv) <= 1:
        print "main.py demofile.dem"
        sys.exit()
    
    if demo.open(filename):
        print "Beginning dump"
        demo.register_on_gameevent(99, player_purchase)
        demo.register_on_gameevent(151, flashbang_detonate)
        demo.dump()