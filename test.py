from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QGridLayout, QPushButton,QItemDelegate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import numpy as np
import pyqtgraph as pg
import h5py

class Delegate(QItemDelegate):
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

class Table(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.setFixedSize(740, 700)
        choices = ['1', '2', '3','4','5']
        data1 = np.random.random(size=(5,5)).round(4)
        data2 = np.zeros((5,2))
        table = np.concatenate((data1, data2),axis = 1)
        table[:,1] = np.ones(5)

        self.model = Model(table)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(1, Delegate(self,choices))
        for row in range(len(table)):
            self.table.openPersistentEditor(self.model.index(row, 1))

        self.btnLoad = QPushButton("load")
        self.btnLoad.clicked.connect(self.load_data)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.table,0,0,5,5)
        self.grid.addWidget(self.btnLoad,5,0,1,1)
        
        self.graphWidget = pg.PlotWidget()
        self.grid.addWidget(self.graphWidget,2,0,3,5)
        
        self.btn_graph= QPushButton("Graph")
        self.btn_graph.clicked.connect(self.draw_graph)
        self.grid.addWidget(self.btn_graph,5,1,1,1)
        
    def draw_graph(self):
        self.graphWidget.clear()
        rows = [index.column() for index in self.table.selectedIndexes()]
        rows = list(dict.fromkeys(rows))
        x = self.model.table[:,rows[-1]]
        y = self.model.table[:,rows[-2]]
        self.graphWidget.plot(x, y)
    
    def save_file(self):
        with h5py.File('file.h5', 'w') as hf:
            hf.create_dataset("table_array",  data=self.model.table)
        
if __name__=="__main__":
    app = QApplication([])
    w = Table()
    w.show()
    app.exec_()