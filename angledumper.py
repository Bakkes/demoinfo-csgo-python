'''
Created on Jul 13, 2014

@author: Chris
'''
from demodump import DemoDump
from netmessages_public_pb2 import *
import struct

class AngleDumper(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        if self.demo.open(filename):
            self.demo.register_on_netmsg(net_SetConVar, self.set_convar)
            self.demo.register_on_netmsg(net_StringCmd, self.string_cmd)
            self.demo.register_on_netmsg(svc_BSPDecal, self.decal)
            self.demo.register_on_netmsg(svc_PacketEntities, self.packet_entities)
            self.demo.register_on_netmsg(svc_SendTable, self.send_table)
            self.demo.register_on_netmsg(svc_CreateStringTable, self.create_table)
            self.demo.register_on_netmsg(svc_UpdateStringTable, self.update_table)
            self.demo.dump()
            
    def decal(self, cmd, data):
        decal = CSVCMsg_BSPDecal()
        decal.ParseFromString(data)
        #print "%i to (%f, %f, %f)" % (decal.entity_index, decal.pos.x, decal.pos.y, decal.pos.z)
        
    def set_convar(self, cmd, data):
        d2 = CNETMsg_SetConVar()
        d2.ParseFromString(data)
        #for var in d2.convars.cvars:
        #    print "%s: %s" % (var.name, var.value)
        #print len(d2.convars.cvars)
        
    def string_cmd(self, cmd, data):
        c = CNETMsg_StringCmd()
        c.ParseFromString(data)
        #print c.command
    
    def packet_entities(self, cmd, data):
        entities = CSVCMsg_PacketEntities()
        entities.ParseFromString(data)
        #print entities.entity_data
        offset = 0
        entity_id = 0
        
        while True:
            entity_id += 1
            footer = struct.unpack_from("h", entities.entity_data, offset)[0]
            offset += 2
            bool = struct.unpack_from("?", entities.entity_data, offset)[0]
            offset += 1
            custom = struct.unpack_from("?", entities.entity_data, offset)[0]
            offset += 1
            bli = struct.unpack_from("?", entities.entity_data, offset)[0]
            offset += 1
            offset += 6
            
            flag = struct.unpack_from("i", entities.entity_data, offset)[0]
            offset += 4
            name = struct.unpack_from("s", entities.entity_data, offset)[0]

            print footer
            print bool
            print custom
            print bli
            
            print name
            break
            
    def send_table(self, cmd, data):
        print "Send table"
        
    def create_table(self, cmd, data):
        t = CSVCMsg_CreateStringTable()
        t.ParseFromString(data)
        return
        #if t.name == "downloadables":
        #    f = open("test.bin", "wb")
        #    f.write(t.string_data)
        #bool bIsServer, const char *value, int length = -1, const void *userdata = 0
        """
            virtual void Restore( const SaveRestoreFieldInfo_t &fieldInfo, IRestore *pRestore )
    {
        int *pStringIndex = (int *)fieldInfo.pField;
        int nLen = pRestore->ReadInt();
        char *pTemp = (char *)stackalloc( nLen );
        pRestore->ReadString( pTemp, nLen, nLen );
        *pStringIndex = m_pStringTable->AddString( pTemp );
    }
    https://swarm.workshop.perforce.com/files/guest/knut_wikstrom/ValveSDKCodegame_shared/saverestore.h
    https://swarm.workshop.perforce.com/files/guest/knut_wikstrom/ValveSDKCodegame_shared/saverestore_stringtable.h
    
    """
        #print t.user_data_fixed_size
        #print len(t.string_data)
        import binascii
        for i in range(0, t.num_entries):
            f = open('test2.bin', 'w')
            for x in range(0 ,len(t.string_data)-4):
                struct_fmt = "i"
                struct_len = struct.calcsize(struct_fmt)
                struct_unpack = struct.Struct(struct_fmt)
                read = struct_unpack.unpack_from(t.string_data, x)
                if read[0] < 2000 and read[0] > 0:
                    struct_fmt = "%ic" % read[0]
                    struct_unpack = struct.Struct(struct_fmt)
                    txt = struct_unpack.unpack_from(t.string_data, x + struct_len)
                    
                    tot = ""
                    for t2 in txt:
                        tot += t2
                    f.write("index: %i: size: %i: %s" % (x, read[0], tot))
                    print "index: %i: size: %i: %s" % (x, read[0], tot)
                #print read
            return
        print "Create table"
        
    def update_table(self, cmd, data):
        table = CSVCMsg_UpdateStringTable()
        table.ParseFromString(data)
        string_data = table.string_data
        print "Update table"
if __name__ == '__main__':
    # demo = DemoDump()
    filename = "gotv.dem"
     
    hlfinder = AngleDumper(filename)