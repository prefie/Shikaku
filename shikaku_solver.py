#!/usr/bin/python3

import math
import os
import sys
import threading
import re
from copy import deepcopy

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QWidget, QMessageBox,
                             QHBoxLayout, QFileDialog, QAction, QVBoxLayout, QGridLayout, QSlider, QLineEdit,
                             QPushButton, QLabel)

import shikaku_generator
from modules.solver import Solver
from modules.task import Task

BACK_COLORS = {
    -1: QColor('white'),
    0: QColor('cyan'),
    1: QColor('blue'),
    2: QColor('sea green'),
    3: QColor('yellow'),
    4: QColor('orange'),
    5: QColor('purple'),
    6: QColor('brown'),
    7: QColor('pink'),
    8: QColor('grey'),
    9: QColor('maroon'),
    10: QColor('red'),
    11: QColor('darkGreen'),
    12: QColor('darkCyan'),
    13: QColor('darkBlue'),
    14: QColor('white')
}


class GuiParallelepiped(QFrame):

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self._task = deepcopy(task)

        self.pen = QPen(QColor(0, 0, 0))
        self.pen.setWidth(3)
        self.brush = QBrush(QColor(255, 255, 0, 255))

        self._size_cube = 50
        self.painter = QPainter()
        self._rect = {}
        self._generate_rect()
        self._init_ui()

    @staticmethod
    def create_rect(dx, dy, angle1, angle2, offset_x, offset_y):
        rec = QPolygonF()

        left_bottom = QPointF(offset_x, offset_y)

        x1 = dx * math.cos(math.radians(angle2))
        y1 = dy * math.sin(math.radians(angle2))
        right_bottom = QPointF(x1 + offset_x, y1 + offset_y)

        x = dx * math.cos(math.radians(angle1))
        y = dy * math.sin(math.radians(angle1))
        left_top = QPointF(x + offset_x, -y + offset_y)
        right_top = QPointF(x + x1 + offset_x, -y + y1 + offset_y)

        rec.append(left_bottom)
        rec.append(right_bottom)
        rec.append(right_top)
        rec.append(left_top)
        return rec

    def _init_ui(self):
        self.setFixedSize(
            (self._size_cube * self._task.size_x +
             self._size_cube * self._task.size_z * math.cos(math.radians(30)) + 2),
            (self._size_cube * self._task.size_y +
             self._size_cube * self._task.size_z * math.sin(math.radians(30)) + 2))

    def _generate_rect(self):
        offset_x = 0
        offset_y = self._size_cube * self._task.size_z * math.sin(math.radians(30))
        angle = 30
        for z in range(self._task.size_z):
            for x in range(self._task.size_x):
                rec = self.create_rect(self._size_cube, self._size_cube, angle, 0, offset_x, offset_y)
                self._rect[(x, 0, z, 'xz')] = rec
                offset_x += self._size_cube
            offset_y -= self._size_cube * math.sin(math.radians(angle))
            offset_x = self._size_cube * math.cos(math.radians(angle)) * (z + 1)

        offset_x = 0
        offset_y = self._size_cube * self._task.size_z * math.sin(math.radians(30)) + self._size_cube
        angle = 90
        for y in range(self._task.size_y):
            for x in range(self._task.size_x):
                rec = self.create_rect(self._size_cube, self._size_cube, angle, 0, offset_x, offset_y)
                self._rect[(x, y, 0, 'xy')] = rec
                offset_x += self._size_cube
            offset_y += self._size_cube * math.sin(math.radians(angle))
            offset_x = 0

        offset_x = self._task.size_x * self._size_cube
        offset_y = self._size_cube * self._task.size_z * math.sin(math.radians(30))
        angle = 30
        for y in range(self._task.size_y):
            for z in range(self._task.size_z):
                rec = self.create_rect(self._size_cube, self._size_cube, angle, 90, offset_x, offset_y)
                self._rect[(self._task.size_x - 1, y, z, 'yz')] = rec
                offset_x += self._size_cube * math.cos(math.radians(angle))
                offset_y -= self._size_cube * math.sin(math.radians(angle))
            offset_y = (self._size_cube * self._task.size_z * math.sin(math.radians(30)) +
                        self._size_cube * (y + 1))
            offset_x = self._task.size_x * self._size_cube

    def paintEvent(self, e):

        self.painter.begin(self)
        self._draw()
        self.painter.end()

    def _draw(self):
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

        for i in self._rect:
            id_color = self._task.solution[i[0]][i[1]][i[2]]
            color = BACK_COLORS[id_color % (len(BACK_COLORS) - 1)]
            brush = QBrush(color)
            self.painter.setBrush(brush)
            self.painter.drawPolygon(self._rect[i])

            if self._task.field[i[0]][i[1]][i[2]] != -1:
                rect = self._rect[i].boundingRect()
                self.painter.drawText(rect, Qt.AlignCenter,
                                      str(self._task.field[i[0]][i[1]][i[2]]))


def thread(func):
    """Запускает функцию в отдельном потоке"""

    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.start()

    return wrapper


class input_dialog(QWidget):
    def __init__(self):
        super(input_dialog, self).__init__()
        self.setWindowTitle('Создание новой головоломки Shikaku')

        self.width = QLineEdit(self)
        self.height = QLineEdit()
        self.depth = QLineEdit()
        self.puzzle_name = QLineEdit()
        self.solution_name = QLineEdit()

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)
        continue_button = QPushButton("Создать")
        continue_button.clicked.connect(self._continue_handler)

        main_layout = QGridLayout()
        main_layout.addWidget(QLabel('Ширина'), 0, 0)
        main_layout.addWidget(self.width, 0, 1)

        main_layout.addWidget(QLabel('Высота'), 1, 0)
        main_layout.addWidget(self.height, 1, 1)

        main_layout.addWidget(QLabel('Глубина'), 2, 0)
        main_layout.addWidget(self.depth, 2, 1)

        main_layout.addWidget(QLabel('Имя файла головоломки'), 3, 0)
        main_layout.addWidget(self.puzzle_name, 3, 1)

        main_layout.addWidget(QLabel('Имя файла решения'), 4, 0)
        main_layout.addWidget(self.solution_name, 4, 1)

        self.path = QLabel()
        self.path.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        main_layout.addWidget(QLabel('Директория для сохранения\nголоволомки и её решения:'), 5, 0)
        main_layout.addWidget(self.path, 5, 1)
        dir_button = QPushButton('...')
        dir_button.clicked.connect(self._path_handler)
        main_layout.addWidget(dir_button, 5, 2)

        main_layout.addWidget(cancel_button, 6, 1)
        main_layout.addWidget(continue_button, 6, 2)

        self.width.setPlaceholderText('1')
        self.height.setPlaceholderText('1')
        self.depth.setPlaceholderText('1')
        self.puzzle_name.setPlaceholderText('shikaku_puzzle.txt')
        self.solution_name.setPlaceholderText('shikaku_solution.txt')
        self.path.setText(os.path.abspath(os.curdir))

        self.setLayout(main_layout)

    def _continue_handler(self):
        try:
            w = int(self.width.text()) if self.width.text() else 1
            h = int(self.height.text()) if self.width.text() else 1
            d = int(self.depth.text()) if self.width.text() else 1
        except ValueError:
            # TODO: Если некорректные параметры?
            return
        puzzle_name = self.path.text() + '\\'
        puzzle_name += self.puzzle_name.text() if self.puzzle_name.text() else 'shikaku_puzzle.txt'
        solution_name = self.path.text() + '\\'
        solution_name += self.solution_name.text() if self.solution_name.text() else 'shikaku_solution.txt'
        shikaku_generator.generate_puzzle(w, h, d, puzzle_name, solution_name)
        self.close()

    def _path_handler(self):
        path = QFileDialog.getExistingDirectory()
        self.path.setText(path)


class MainForm(QMainWindow):
    solver_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.solver_signal.connect(self._update)

        self._task = None
        self._init_ui()
        self._flag = True

    def _init_ui(self):
        self.setMinimumSize(1200, 500)
        self.setGeometry(0, 0, 1200, 500)
        self.setWindowTitle('Shikaku')

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QVBoxLayout(centralWidget)
        self.hBox = QHBoxLayout()
        self.mainLayout.addLayout(self.hBox)

        self.hBox.addStretch(1)
        self.grid = QGridLayout()
        self.hBox.addLayout(self.grid)
        self.hBox.addStretch(1)

        self.parallelepipeds = []

        self.scroll_x = QSlider(Qt.Horizontal)
        self.mainLayout.addWidget(self.scroll_x)
        self.scroll_x.setRange(0, 0)

        self.scroll_y = QSlider()
        self.scroll_y.setRange(0, 0)

        self.scroll_z = QSlider()
        self.scroll_z.setRange(1, 1)
        self.scroll_z.setMinimum(1)
        self.hBox.addWidget(self.scroll_y)
        self.hBox.addWidget(self.scroll_z)

        self._activate_scrolls()  # !!!!!!!!!!!!!!!

        create_action = QAction('&Создать', self)
        create_action.setShortcut('Ctrl+N')
        create_action.setStatusTip('Сгенерировать новую головоломку')
        create_action.triggered.connect(self._create_handler)

        open_file_action = QAction('&Открыть', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.setStatusTip('Открыть файл с головоломкой')
        open_file_action.triggered.connect(self._open_file_dialog)

        solve_action = QAction('&Решить', self)
        solve_action.setShortcut('Ctrl+S')
        solve_action.setStatusTip('Решить головоломку')
        solve_action.triggered.connect(self.solver_handler)

        self.statusBar()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&Меню')
        file_menu.addAction(create_action)
        file_menu.addAction(open_file_action)
        file_menu.addAction(solve_action)

        self.msg = QMessageBox()
        self.msg.addButton('Ок', QMessageBox.RejectRole)

        self.show()

    def _activate_scrolls(self):
        self.scroll_x.valueChanged.connect(self._scroll_handler)
        self.scroll_y.valueChanged.connect(self._scroll_handler)
        self.scroll_z.valueChanged.connect(self._scroll_handler)

    def _deactivate_scrolls(self):
        self.scroll_x.valueChanged.disconnect(self._scroll_handler)
        self.scroll_y.valueChanged.disconnect(self._scroll_handler)
        self.scroll_z.valueChanged.disconnect(self._scroll_handler)

    def _open_file_dialog(self):
        a = QFileDialog.getOpenFileName(self, 'Open file', '')
        filename = a[0]

        if filename:
            self._get_task(filename)

    def _create_handler(self):
        self.new_window = input_dialog()
        self.new_window.show()

    def _get_task(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read()
                field = _parse_puzzle(data)
        except Exception as e:
            self.msg.setWindowTitle('Ошибка при открытии головоломки/решения:')
            self.msg.setText(e.args[0])
            self.msg.show()
        else:
            self._task = Task(field, solution=field)
            self._update()

    ''''@thread
    def _get_task(self, signal, filename):
        with open(filename, 'r') as f:
            data = f.read()
            field = parse_puzzle(data)
            s = Solver(Task(field))
            result = s.solve()
            signal.emit(result, s.task)'''

    '''def _signal_handler(self, result, task):
        if not result:
            return
            # TODO: Если головоломка не решена?
        self._task = task

        self._clear_parallelepipeds()

        self.scroll_x.setRange(0, self._task.size_x - 1)
        self.scroll_y.setRange(0, self._task.size_y - 1)
        self.scroll_z.setRange(1, self._task.size_z)
        self.scroll_z.setValue(self._task.size_z)'''

    def _clear_parallelepipeds(self):
        for p in self.parallelepipeds:
            p.close()
            self.grid.removeWidget(p)
        self.parallelepipeds.clear()

    def _update(self):
        self._deactivate_scrolls()

        self._clear_parallelepipeds()
        paral = GuiParallelepiped(self._task)
        self.parallelepipeds.append(paral)
        self.grid.addWidget(paral, 0, 0)

        self.scroll_x.setRange(0, self._task.size_x - 1)
        self.scroll_y.setRange(0, self._task.size_y - 1)
        self.scroll_z.setRange(1, self._task.size_z)
        self.scroll_x.setValue(0)
        self.scroll_y.setValue(0)
        self.scroll_z.setValue(self._task.size_z)

        self._activate_scrolls()

    @thread
    def solver_handler(self, _):
        task = deepcopy(self._task)
        solver = Solver(task)
        solver.solve()
        self._task = task
        self.solver_signal.emit()

    def _scroll_handler(self):
        self._clear_parallelepipeds()

        dx = self.scroll_x.value()
        dy = self.scroll_y.value()
        dz = self.scroll_z.value()

        tasks = [i for i in self._cut_task(self._task, dx, dy, dz)]
        if tasks[1] is not None:
            paral = GuiParallelepiped(tasks[1])
            self.parallelepipeds.append(paral)
            self.grid.addWidget(paral, 1, 0)

        if tasks[0] is not None:
            paral = GuiParallelepiped(tasks[0])
            self.parallelepipeds.append(paral)
            self.grid.addWidget(paral, 0, 0)

        if tasks[3] is not None:
            paral = GuiParallelepiped(tasks[3])
            self.parallelepipeds.append(paral)
            self.grid.addWidget(paral, 1, 1)

        if tasks[2] is not None:
            paral = GuiParallelepiped(tasks[2])
            self.parallelepipeds.append(paral)
            self.grid.addWidget(paral, 0, 1)

    def _cut_task(self, task, dx=0, dy=0, dz=0):
        def is_empty(array):
            if not array:
                return True
            for x in array:
                if not x:
                    return True
                for y in x:
                    if not y:
                        return True
            return False

        task = deepcopy(task)
        for x in range(task.size_x):  # Глубина
            for y in range(task.size_y):
                task.field[x][y] = task.field[x][y][:dz]
                task.solution[x][y] = task.solution[x][y][:dz]

        fields = [task.field[:dx], task.field[dx:]]
        solutions = [task.solution[:dx], task.solution[dx:]]

        for i in range(len(fields)):
            field = deepcopy(fields[i])
            solution = deepcopy(solutions[i])
            for x in range(len(field)):
                field[x] = fields[i][x][:dy]
                solution[x] = solutions[i][x][:dy]

            yield None if is_empty(field) else Task(field, solution)

            field = deepcopy(fields[i])
            solution = deepcopy(solutions[i])
            for x in range(len(field)):
                field[x] = fields[i][x][dy:]
                solution[x] = solutions[i][x][dy:]

            yield None if is_empty(field) else Task(field, solution)

'''
def parse_puzzle(text):
    field = text.split('\n\n')

    error = ValueError('The puzzle is incorrect')

    result = []
    for x in range(len(field)):
        plane = field[x].split('\n')
        dy = []
        for y in range(len(plane)):
            line = plane[y].split()
            dz = list(map(lambda i: -1 if i == '-' else int(i), line))

            dy.append(dz)
        result.append(dy)

    count_dy = len(result[0])
    count_dz = len(result[0][0])
    for x in range(len(result)):
        if len(result[x]) != count_dy:
            raise error
        for y in range(len(result[x])):
            if len(result[x][y]) != count_dz:
                raise error

    return result
'''


'''
def _parse_puzzle(text):
    p_text = text.split('\n')
    field = [[]]

    dx = 0
    dy = 0
    for j in range(len(p_text)):
        string = p_text[j]
        if not string:
            dx += 1
            dy = 0
            field.append([])
            continue

        str_split = re.split('\t| ', string)
        field[dx].append([])

        sym = 0
        for k in range(len(str_split)):
            element = str_split[k]
            digit_str = ''
            for i in range(len(element)):
                if element[i] == '\t':
                    if digit_str != '':
                        field[dx][dy].append(int(digit_str))
                        digit_str = ''
                    continue

                if element[i] == '-' and len(element) == 1:
                    field[dx][dy].append(-1)
                elif element[i].isdigit():
                    digit_str += element[i]

                elif element[i] == '*':
                    field[dx][dy].append(int(digit_str))
                    digit_str = ''
                else:
                    raise ValueError(f'{j + 1}:{sym + 1}\n{string}:{element[i]}')
                sym += 1

            if digit_str != '':
                field[dx][dy].append(int(digit_str))

        dy += 1

    count_dy = len(field[0])
    count_dz = len(field[0][0])
    for x in range(len(field)):
        if len(field[x]) != count_dy:
            raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}')
        for y in range(len(field[x])):
            if len(field[x][y]) != count_dz:
                raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}, y = {y}')

    return field'''


def _parse_puzzle(text):
    p_text = text.split('\n')
    field = [[]]

    dx = 0
    dy = 0
    for j in range(len(p_text)):
        string = p_text[j]
        if not string:
            dx += 1
            dy = 0
            field.append([])
            continue

        field[dx].append([])
        digit_str = ''
        for i in range(len(string)):
            if string[i] == '\t' or string[i] == ' ':
                if digit_str != '':
                    field[dx][dy].append(int(digit_str))
                    digit_str = ''
                continue

            if string[i] == '-':
                if i - 1 >= 0 and string[i - 1] != '\t' and string[i - 1] != ' ':
                    raise ValueError(
                        f'строка:символ\n\n{j + 1}:{i + 1}\n{string}:{string[i]}')
                if i + 1 < len(string) and string[i + 1] != '\t' and string[i + 1] != ' ':
                    raise ValueError(
                        f'строка:символ\n\n{j + 1}:{i + 2}\n{string}:{string[i + 1]}')
                field[dx][dy].append(-1)
            elif string[i].isdigit():
                digit_str += string[i]

            elif string[i] == '*':
                if len(digit_str) == 0:
                    raise ValueError(
                        f'строка:символ\n\n{j + 1}:{i + 1}\n{string}:{string[i]}')
                if i + 1 < len(string) and string[i + 1] != '\t' and string[i + 1] != ' ':
                    raise ValueError(
                        f'строка:символ\n\n{j + 1}:{i + 2}\n{string}:{string[i + 1]}')
                field[dx][dy].append(int(digit_str))
                digit_str = ''
            else:
                raise ValueError(
                    f'строка:символ\n\n{j + 1}:{i + 1}\n{string}:{string[i]}')

        if digit_str != '':
            field[dx][dy].append(int(digit_str))

        dy += 1

    count_dy = len(field[0])
    count_dz = len(field[0][0])
    for x in range(len(field)):
        if len(field[x]) != count_dy:
            raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}')
        for y in range(len(field[x])):
            if len(field[x][y]) != count_dz:
                raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}, y = {y}')

    return field


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    sys.exit(app.exec_())
