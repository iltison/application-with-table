import numpy as np

dir_filename = 'second/in.txt'

def read_txt(filename):
    """
    Чтение текстового файла и запись в массив

    args:
        filename : расположение txt файла
    return:
        array : полученный из текстового документа массив
    """
    f = open(filename, 'r')
    array = np.array([list(map(int,line.strip().split())) for line in f])
    f.close()
    return array

def find_coef(array):
    """
    Нахождение корней системы уравнений
    Уравнение для параболы : y = c_0 + c_1 * x + c_2 * x^2

    args:
        array : массив с координатами
    return:
        coef : полученные коэффициенты 
    """
    A = array[:,0]
    A = np.insert(A, 0, 0, axis=0)
    A = np.power(A.reshape(-1,1), [0,1,2])
    B = array[:,1]
    B = np.insert(B, 0, 0, axis=0)
    coef = np.linalg.lstsq(A, B,rcond=None)[0]
    return coef

def find_roots(coef):
    """
    Нахождение при каком значении х, уравнение имеет корни

    args:
        coef : коэффициенты для уравнения параболы
    return:
        root : найденный корень, который не равен 0. Парабола в двух точках равняется нулю 
    """
    roots = np.poly1d([coef[2], coef[1], coef[0]]).r
    for root in roots:
        root = round(root)
        if root != 0:
            return root

if __name__=="__main__":
    array = read_txt(dir_filename)
    coef = find_coef(array)
    distance = find_roots(coef)
    print(f'Расстояник на которое улетит камень = {distance}')

