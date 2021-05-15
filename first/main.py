from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QGridLayout, QPushButton,QItemDelegate,QFileDialog
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui 
import numpy as np
import pyqtgraph as pg
import h5py

from setting import size_array, preload_read_file, preload_filename

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
        
        value = editor.currentText()
        model = index.model()
        model.table[index.row()][index.column()] = value

    def setModelData(self, editor, model, index):
        """
        Изменяет значения таблицы на значения полученные из выпадающего меню

        args:
            editor : поле со списком
            model : таблица
            index : индекс, в котором находится поле со списком
        """

        index_arg = model.index(index.row(), model.arg_column)
        value = editor.currentText()
        model.setData(index, value, QtCore.QVariant(value))
        model.setData(index_arg, value, QtCore.QVariant(value))
    
    
class Model(QtCore.QAbstractTableModel):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.selected_column_arg = 1
        self.selected_column_sum = 0

        self.arg_column = 0
        self.sum_column = 0

    def rowCount(self, parent):
        """
        Получение количества строк таблицы
        """
        return len(self.table)

    def columnCount(self, parent):
        """
        Получение количества столбцов таблицы
        """
        cnt_columns = len(self.table[0])
        self.arg_column = cnt_columns - 2
        self.sum_column = cnt_columns - 1
        return cnt_columns

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        Получение названия заголовка

        args:
            section : секция
            orientation : ориентация
        return:
            возвращает название заголовка
        """
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == self.sum_column:
                return 'Сумма 1-ого столбца'
            if section == self.arg_column:
                return 'Квадрат 2-ого столбца'
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

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

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        Получение значения массива соответствующее индексу поля таблицы

        args:
            index : индекс, в котором находится поле
            role : роль с указанием типа данных
        return:
            значение массивы соответствующее индексу поля
        """
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.BackgroundRole and index.column() == 0:
            if self.table[row][column] >= 0:
                return QtGui.QBrush(QtCore.Qt.green)
            else:
                return QtGui.QBrush(QtCore.Qt.red)

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == self.arg_column:
                self.table[row][column] = np.power(self.table[row,self.selected_column_arg],2)
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
        
        self.setFixedSize(740, 800)

        self.grid = QGridLayout(self)
        self.table = QTableView()
        self.btn_save = QPushButton("Save")
        self.btn_load= QPushButton("Load")
        self.btn_graph= QPushButton("Graph")
        self.graphWidget = pg.PlotWidget()

        self.grid.addWidget(self.table,0,0,4,4)
        self.grid.addWidget(self.graphWidget,4,0,2,4)
        self.grid.addWidget(self.btn_save,6,0,1,2)
        self.grid.addWidget(self.btn_load,7,0,1,4)
        self.grid.addWidget(self.btn_graph,6,2,1,2)

class main_window(Ui_MainWindow, QWidget):
    """
    Класс главного окна 
    """
    def __init__(self, parent=None):
        """
        Инициализация GUI

        args:
        self : Виджеты
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        load_table_data = self.preload_data()
        self.create_table(load_table_data)

        self.btn_save.clicked.connect(self.save_button_handler)
        self.btn_graph.clicked.connect(self.graph_button_handler)
        self.btn_load.clicked.connect(self.load_button_handler)

    def create_table(self, table_data):
        """
        Создание таблицы 

        args:
        table_data : данные для таблицы
        """
        self.model = Model(table_data)
        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(1, Delegate(self))
        for row in range(len(table_data)):
            self.table.openPersistentEditor(self.model.index(row, 1))
        self.table.setSelectionBehavior(QTableView.SelectColumns)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        header = self.table.horizontalHeader()
        for column in range(table_data.shape[1]):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents) 

    def preload_data(self):
        """
        Загрузка начального датасета
        
        preload_read_file : True - чтение из файла
                            False - создание нового массива
        preload_filename : Расположение файла с датасетом 
        настройки расположены в файле setting
            
        """
        if preload_read_file:
            dataset = self.read_dataset_file(preload_filename)
        else:
            dataset = self.create_random_array()
        return dataset

    def read_dataset_file(self, filename):
        """
        Чтение файла

        args:
            filename : расположение файла 
        """
        with h5py.File(filename, 'r') as f:
            dataset = f['table_array'][:]
            return dataset

    def save_dataset_file(self, filename):
        """
        Сохранение файла

        args:
            filename : расположение файла 
        """
        with h5py.File(filename, 'w') as hf:
            hf.create_dataset("table_array",  data=self.model.table)

    def create_random_array(self):
        """
        Создание рандомного массива

        size_array: размер массива
        настройка расположена в файле setting

        return:
            dataset : массив со случайными значениями
        """
        dataset = np.random.randint(low=-1000, high=1000, size=size_array)
        return dataset

    def load_button_handler(self):
        """
        Обработчик кнопки загрузки
        """
        try:
            filename = self.openFileNameDialog()
            load_table_data = self.read_dataset_file(filename=filename)
            self.create_table(load_table_data)
        except:
            pass

    def save_button_handler(self):
        """
        Обработчик кнопки сохранения
        """
        filename = self.saveFileDialog()
        self.save_dataset_file(filename=filename)
        
    def graph_button_handler(self):
        """
        Обработчик кнопки создания графика
        """
        try:
            self.graphWidget.clear()
            columns = [index.column() for index in self.table.selectedIndexes()]
            columns = list(dict.fromkeys(columns))
            x = self.model.table[:,columns[-1]]
            y = self.model.table[:,columns[-2]]
            self.graphWidget.plot(x, y)
        except:
            pass
            #raise Exception('select 2 columns') 
    
    def openFileNameDialog(self):  
        """
        Меню для открытия файла

        return:
            fileName : возвращает расположение файла
        """  
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",
        "Hierarchical Data Format (*.hdf5)", options=options)
        if fileName:
            return fileName
 
    def saveFileDialog(self):  
        """
        Меню для сохранения файла

        return:
            fileName : возвращает расположение файла
        """   
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, format_file = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "",
        "Hierarchical Data Format (*.hdf5)", options=options)
        
        if format_file == 'Hierarchical Data Format (*.hdf5)' and fileName[-5:] != '.hdf5':
            fileName = fileName + '.hdf5'
            return fileName
        if format_file == 'Hierarchical Data Format (*.hdf5)' and fileName[-5:] == '.hdf5':
            return fileName
    
        
if __name__=="__main__":
    app = QApplication([])
    w = main_window()
    w.show()
    app.exec_()