# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'treeview.ui'
#
# Created: Tue Jul 15 20:53:48 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
    
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(852, 521)
        self.treeView = QtGui.QTreeView(Form)
        self.treeView.setGeometry(QtCore.QRect(0, 290, 851, 231))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.tableView = QtGui.QTableWidget(Form)
        self.tableView.setGeometry(QtCore.QRect(0, 0, 851, 281))
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.tableView.setColumnCount(3)
        self.tableView.setRowCount(100)
        self.tableView.verticalHeader().setVisible(False)
        for i in range(0, 100):
            print "test"
            self.tableView.setItem(i, 0, QtGui.QTableWidgetItem(QtCore.QString("%i" % i)))
            self.tableView.setItem(i, 1, QtGui.QTableWidgetItem(QtCore.QString("a")))
            self.tableView.setItem(i, 2, QtGui.QTableWidgetItem(QtCore.QString("b")))
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
    
