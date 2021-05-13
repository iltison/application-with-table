from PyQt5 import QtWidgets, QtCore,QtGui
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
class Delegate(QtWidgets.QItemDelegate):
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices

    def createEditor(self, parent, option, index):
        self.editor = QtWidgets.QComboBox(parent)
        self.editor.addItems(self.items)
        return self.editor

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.QVariant(value))
    
    
class Model(QtCore.QAbstractTableModel):
    def __init__(self, table):
        super().__init__()
        self.table = table

    def rowCount(self, parent):
        return len(self.table)

    def columnCount(self, parent):
        return len(self.table[0])

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return str(self.table[index.row()][index.column()])

    def setData(self, index, value, role):
        def is_digit(s):
            try:
                float(s)
                return True
            except ValueError:
                return False
 
        if not is_digit(value):                                               
            return False                                                     
    
        if not index.isValid():
            return False

        #if role != QtCore.Qt.EditRole:
            #return False

        self.table[index.row()][index.column()] = value
        self.table[:,5] = self.table[:,1]                           
        self.table[:,6] = self.table[:,0].sum()   

        self.dataChanged.emit(index, index)
        return True

class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        # set combo box choices:
        choices = ['1', '2', '3','4','5']
        # create table data:
        data1 = np.random.random(size=(5,5)).round(4)
        data2 = np.zeros((5,2))
        table = np.concatenate((data1, data2),axis = 1)
        table[:,1] = np.ones(5)
        # create table view:
        
        self.model = Model(table)

        self.tableView = QtWidgets.QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegateForColumn(1, Delegate(self,choices))
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.tableView.horizontalHeader().setStretchLastSection(True )
        
        # make combo boxes editable with a single-click:
        for row in range(len(table)):
            self.tableView.openPersistentEditor(self.model.index(row, 1))
            #self.model.setData(self.model.index(row, 1), choices[0], QtCore.QVariant(self.model.index(row, 1)))
        # initialize

        self.button = QPushButton("Push for Window",self)
        self.button.resize(100,32)
        self.button.move(50, 180) 

        self.setCentralWidget(self.tableView)
        #self.setCentralWidget(self.button)
        

    def button_clicked():
        print("Button 1 clicked")
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    app.exec_()