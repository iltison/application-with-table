from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QGridLayout, QPushButton,QItemDelegate
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
        """
        Создает поле со списком внутри родительского элемента

        args:
            parent : контейнер с выпадающем списком
        not used args:
            option : параметры, использованные для рисования элемента в виде виджета
            index : индекс, в котором поле со списком будет добавлено
        return:
            self.editor : выпадающий список 
        """
        self.editor = QtWidgets.QComboBox(parent)
        self.editor.addItems(self.items)
        return self.editor

    def setEditorData(self, editor, index):
        """
        Изменяет при создание значения таблицы на значения выпадающего списка 

        args:
            editor : поле со списком
            index : индекс, в котором находится поле со списком
        """
        index.model().table[index.row()][index.column()] = editor.currentText()

    def setModelData(self, editor, model, index):
        """
        Изменяет значения таблицы на значения полученные из выпадающего меню

        args:
            editor : поле со списком
            model : таблица
            index : индекс, в котором находится поле со списком
        """
        value = editor.currentText()
        model.setData(index, value, QtCore.QVariant(value))
    
    
class Model(QtCore.QAbstractTableModel):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.selected_column_arg = 1
        self.selected_column_sum = 0

        self.arg_column = 5
        self.sum_column = 6

    def rowCount(self, parent):
        """
        Получение количества строк таблицы
        """
        return len(self.table)

    def columnCount(self, parent):
        """
        Получение количества столбцов таблицы
        """
        return len(self.table[0])

    def flags(self, index):
        """
        Доступные флаги для ячеек

        args:
            index : индекс, в котором находится поле
        return:
            возвращает флаги
        """
        column = index.column()
        if column in (self.arg_column,self.sum_column):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 
        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 

    def data(self, index, role):
        """
        Получение значения массива соответствующее индексу поля таблицы

        args:
            index : индекс, в котором находится поле
            role : роль с указанием типа данных
        return:
            значение массивы соответствующее индексу поля
        """
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if column == self.arg_column:
                self.table[row][column] = self.table[row,self.selected_column_arg]
                return str(self.table[row][column])

            if column == self.sum_column:
                self.table[row][column] = self.table[:,self.selected_column_sum].sum()
                return str(self.table[row][column].round(4))

            else:
                return str(self.table[row][column])

    def setData(self, index, value, role):
        """
        Отображение значений в таблице

        args:
            index : индекс, в котором находится поле
            value : значение, которое установится в поле
            role : роль с указанием типа данных
        """
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

class Ui_MainWindow(object):
    """
    Класс для создания объектов интерфейса 
    """
    def setupUi(self, MainWindow):
        
        self.setFixedSize(740, 700)

        self.grid = QGridLayout(self)
        self.table = QTableView()
        self.btn_load = QPushButton("Save")
        self.btn_graph= QPushButton("Graph")
        self.graphWidget = pg.PlotWidget()

        self.grid.addWidget(self.table,0,0,5,5)
        self.grid.addWidget(self.graphWidget,2,0,3,5)
        self.grid.addWidget(self.btn_load,5,0,1,1)
        self.grid.addWidget(self.btn_graph,5,1,1,1)

class main_window(Ui_MainWindow, QWidget):
    """
    Класс главного окна 
    """

    def __init__(self, parent=None):
        """Инициализация GUI

        args:
        self : Виджеты
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.reading_file=False

        table = self.load_data(self.reading_file)
        self.model = Model(table)
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(1, Delegate(self))
        for row in range(len(table)):
            self.table.openPersistentEditor(self.model.index(row, 1))
        self.table.setSelectionBehavior(QTableView.SelectColumns)
        self.table.setSelectionMode(QTableView.ContiguousSelection)
        self.btn_load.clicked.connect(self.save_file)
        self.btn_graph.clicked.connect(self.draw_graph)

    def load_data(self, reading_from_file = True):
        """
        Функция загрузки датасета из файла или созданиние нового с случайными значениями 

        args:
            self : main_window object
            reading_from_file : True - чтение из файла
                                False - создание нового массива
        """
        if reading_from_file:
            with h5py.File('file.hdf5', 'r') as f:
                dataset = f['table_array'][:]
                return dataset
        else:
            dataset = np.random.random(size=(5,7)).round(4)
            return dataset

    def draw_graph(self):
        """
        Функция создания графика

        args:
            self : main_window object
        """
        try:
            self.graphWidget.clear()
            columns = [index.column() for index in self.table.selectedIndexes()]
            columns = list(dict.fromkeys(columns))
            x = self.model.table[:,columns[-1]]
            y = self.model.table[:,columns[-2]]
            self.graphWidget.plot(x, y)

        except:
            raise Exception('select 2 columns') 
    
    def save_file(self):
        """
        Функция сохранения массива

        args:
            self : main_window object
        """
        with h5py.File('file.hdf5', 'w') as hf:
            hf.create_dataset("table_array",  data=self.model.table)
        
if __name__=="__main__":
    app = QApplication([])
    w = main_window()
    w.show()
    app.exec_()