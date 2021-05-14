from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QGridLayout, QPushButton,QItemDelegate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import numpy as np
import pyqtgraph as pg
import h5py

class Delegate(QItemDelegate):
    def __init__(self, owner):
        super().__init__(owner)
        self.items = ['1', '2', '3','4','5']

    def createEditor(self, parent, option, index):
        self.editor = QtWidgets.QComboBox(parent)
        self.editor.addItems(self.items)
        return self.editor

    def setEditorData(self, editor, index):
        index.model().table[index.row()][index.column()] = editor.currentText()

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.QVariant(value))
    
    
class Model(QtCore.QAbstractTableModel):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.selected_column_arg = 1
        self.selected_column_sum = 0

    def rowCount(self, parent):
        return len(self.table)

    def columnCount(self, parent):
        return len(self.table[0])

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            column = index.column()
            row = index.row()
            if column == 5:
                self.table[row][column] = self.table[row,self.selected_column_arg]
                return str(self.table[row][column])

            if column == 6:
                self.table[row][column] = self.table[:,self.selected_column_sum].sum()
                return str(self.table[row][column].round(4))

            else:
                return str(self.table[row][column])

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

        self.table[index.row()][index.column()] = value 
        self.dataChanged.emit(index, index)
        return True

class Table(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.setFixedSize(740, 700)
        table = self.load_file(reading_from_file=False)
        self.model = Model(table)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(1, Delegate(self))
        for row in range(len(table)):
            self.table.openPersistentEditor(self.model.index(row, 1))

        self.btnLoad = QPushButton("save")
        self.btnLoad.clicked.connect(self.save_file)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.table,0,0,5,5)
        self.grid.addWidget(self.btnLoad,5,0,1,1)
        
        self.graphWidget = pg.PlotWidget()
        self.grid.addWidget(self.graphWidget,2,0,3,5)
        
        self.btn_graph= QPushButton("Graph")
        self.btn_graph.clicked.connect(self.draw_graph)
        self.grid.addWidget(self.btn_graph,5,1,1,1)

    def load_file(self, reading_from_file = True):
        if reading_from_file:
            with h5py.File('file.hdf5', 'r') as f:
                dataset = f['table_array'][:]
                return dataset
        else:
            dataset = np.random.random(size=(5,7)).round(4)
            return dataset

    def draw_graph(self):
        self.graphWidget.clear()
        rows = [index.column() for index in self.table.selectedIndexes()]
        rows = list(dict.fromkeys(rows))
        x = self.model.table[:,rows[-1]]
        y = self.model.table[:,rows[-2]]
        self.graphWidget.plot(x, y)
    
    def save_file(self):
        with h5py.File('file.hdf5', 'w') as hf:
            hf.create_dataset("table_array",  data=self.model.table)
        
if __name__=="__main__":
    app = QApplication([])
    w = Table()
    w.show()
    app.exec_()