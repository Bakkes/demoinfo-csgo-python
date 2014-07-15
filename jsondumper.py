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

class JSONDumper(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        self.callback = None
        if self.demo.open(filename):
            for t in _DUMPED_TYPES:
                self.demo.register_on_netmsg(t, self.on_netmsg)
            
    
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

        print "test"
        sys.exit(app.exec_())
    
    def selection_changed(self, current, previous):
        selected_item = self.tablemodel.items[current.row()]
        
        self.ex.treeView.setModel(selected_item.treeview_model)
        
class DemoModel(object):
    def __init__(self, tick, type, size, data):
        self.tick = tick
        self.type = type
        self.size = size
        self.data = data
        
    @property
    def treeview_model(self):
        model = JSONTreeModel(self.data)
        model.setupModelData()
        return model
    
class KVPair(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        
        
class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, kvpair, header, parentItem):
        self.kvpair = kvpair
        self.parentItem = parentItem
        self.header = header
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 1
    
    def data(self, column):
        if self.kvpair == None:
            if column == 0:
                return QtCore.QVariant(self.header)              
        else:
            if column == 0:
                return QtCore.QVariant("{key}: {value}".format(key=self.item.key, value=self.item.value))
            
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

HORIZONTAL_HEADERS = ("")
class JSONTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(JSONTreeModel, self).__init__(parent)
        self.item_data = data
    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)
        
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        print "DATA"
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return "{key}: {value}".format(key=item.key, value=item.value)

        return QtCore.QVariant()
    
    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        print "row %i" % row
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()
        
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        print "item count: %i" % p_Item.childCount()
        return p_Item.childCount()
    
    def setupModelData(self):
        self.rootItem = TreeItem(KVPair("A", "B"), "", None)
        self.parents = {0: self.rootItem}
        self.rootItem.appendChild(TreeItem(KVPair("A1", "B1"), "", self.rootItem))
        print "setup"
    
    def calc_tree(self, data):
        return
            
            
class TickTableModel(QtCore.QAbstractTableModel): 
    def __init__(self, jsondumper, parent=None, *args): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.jsondumper = jsondumper
        self.jsondumper.callback = self.on_dictitem
        self.items = []
        self.headerdata = ["Tick", "Type", "Size"]
        self.parent_table = parent
        
 
    def on_dictitem(self, dict):
        
        self.items.append(DemoModel(self.jsondumper.demo.current_tick, dict["type"], 0, dict["data"]))
        #print json.dumps(dict, skipkeys=4)
        
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
        
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))"""

if __name__ == '__main__':
    gui = PacketGUI()
    gui.open()
    #
    pass