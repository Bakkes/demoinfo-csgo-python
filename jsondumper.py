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
                    #svc_GameEvent: ("CSVCMsg_GameEvent"),
                    svc_PacketEntities: ("CSVCMsg_PacketEntities"),
                    svc_TempEntities: ("CSVCMsg_TempEntities"),
                    svc_Prefetch: ("CSVCMsg_Prefetch"),
                    svc_Menu: ("CSVCMsg_Menu"),
                    svc_GameEventList: ("CSVCMsg_GameEventList"),
                    svc_GetCvarValue: ("CSVCMsg_GetCvarValue")
                 }

from protojson.pbliteserializer import PbLiteSerializer

class JSONDumper(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        self.callback = None
        if self.demo.open(filename):
            for t in _DUMPED_TYPES:
                self.demo.register_on_netmsg(t, self.on_netmsg)
            for i in range(1, 10000):
                self.demo.register_on_gameevent(i, self.on_event)
    
    def on_event(self, data):
        del data.raw
        name = data.descriptor[1]
        id = data.descriptor[0]
        del data.descriptor
        v = {"name": name, "id": id}
        v["params"] = data.__dict__
        dictz = {"type": "GameEvent (%s)" % name, "data": v}
        if self.callback is not None:
            self.callback(dictz)
    
    def on_netmsg(self, id, data):
        inst = eval(_DUMPED_TYPES[id])()
        inst.ParseFromString(data)
        
        name = _DUMPED_TYPES[id].replace("CNETMsg", "net").replace("CSVCMsg", "svc")
        name = "%s (%i)" % (name, id)
        serializer = PbLiteSerializer()
        dict = {"type": name, "data": serializer.serialize(inst)}
        if self.callback is not None:
            self.callback(dict)
        
import sys
from PyQt4 import QtGui, QtCore
from maingui import Ui_MainWindow
class PacketGUI(object):  
    def __init__(self):
        pass
    
    def open(self):
        app = QtGui.QApplication(sys.argv)
        
        self.ex = Ui_MainWindow()
        self.tablemodel = TickTableModel(JSONDumper("gotv.dem"), parent=self.ex.tableView)
        
        self.ex.tableView.setSortingEnabled(True)
        
        self.tablemodel.jsondumper.demo.dump()
        self.ex.tableView.setModel(self.tablemodel)
        self.ex.tableView.selectionModel().currentChanged.connect(self.selection_changed)

        self.ex.tableView.resizeColumnsToContents()
        self.ex.show()
        sys.exit(app.exec_())
    
    def selection_changed(self, current, previous):
        selected_item = self.tablemodel.items[current.row()]
        
        self.ex.treeView.setHeaderLabels([selected_item.type])
        self.ex.treeView.clear()
        pitems = QtGui.QTreeWidgetItem(self.ex.treeView)
        pitems.setText(0, selected_item.type)
        self.get_recursive(selected_item.data, pitems)

    def get_recursive(self, data, parent):
        if isinstance(data, basestring):
            citems= QtGui.QTreeWidgetItem(parent)
            citems.setText(0, QtCore.QString(data))
        elif (type(data) == list and not isinstance(data, basestring)):
            for item in data:
                self.get_recursive(item, parent)
        else:
            dictz = dict(data)
            
            for k, v in dictz.items():
                citems= QtGui.QTreeWidgetItem(parent)
                if type(v) == dict or (type(v) == list and not isinstance(v, basestring)):
                    citems.setText(0, QtCore.QString(k))
                    self.get_recursive(v, citems)
                else:
                    citems.setText(0, QtCore.QString("{key}: {value}".format(key=k, value=v)))
        
        
            
class DemoModel(object):
    def __init__(self, tick, type, size, data):
        self.tick = tick
        self.type = type
        self.size = size
        self.data = data

    
class TickTableModel(QtCore.QAbstractTableModel): 
    def __init__(self, jsondumper, parent=None, *args): 
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.jsondumper = jsondumper
        self.jsondumper.callback = self.on_dictitem
        self.items = []
        self.headerdata = ["Tick", "Type", "Size"]
        self.parent_table = parent
        
 
    def on_dictitem(self, dict):
        self.items.append(DemoModel(self.jsondumper.demo.current_tick, dict["type"], 0, dict["data"]))
        
    def rowCount(self, parent): 
        return len(self.items) 
 
    def columnCount(self, parent): 
        return len(self.headerdata)
 
    def data(self, index, role): 
        if not index.isValid(): 
            return QtCore.QVariant() 
        elif role != QtCore.Qt.DisplayRole: 
            return QtCore.QVariant() 
        
        if index.column() == 0:
            return QtCore.QVariant(self.items[index.row()].tick)
        elif index.column() == 1:
            return QtCore.QVariant(self.items[index.row()].type)
        elif index.column() == 2:
            return QtCore.QVariant(self.items[index.row()].size)

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

if __name__ == '__main__':
    gui = PacketGUI()
    gui.open()
    #
    pass