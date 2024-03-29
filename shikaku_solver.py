#!/usr/bin/python3

import math
import os
import sys
import threading
from copy import deepcopy
from contextlib import contextmanager

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QWidget,
                             QMessageBox, QHBoxLayout, QFileDialog, QAction,
                             QVBoxLayout, QGridLayout, QSlider, QLineEdit,
                             QPushButton, QLabel, QProgressBar)

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
    13: QColor('darkBlue')
}


@contextmanager
def temp_painter(device):
    painter = QPainter()
    painter.begin(device)
    try:
        yield painter
    finally:
        painter.end()


class GuiParallelepiped(QFrame):

    def __init__(self, field, parent=None):
        super().__init__(parent)
        self._field = field
        self.size_x = len(field)
        self.size_y = len(field[0])
        self.size_z = len(field[0][0])

        self.pen = QPen(QColor(0, 0, 0))
        self.pen.setWidth(3)
        self.brush = QBrush(QColor(255, 255, 0, 255))

        self.size = 40
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
            (self.size * self.size_x +
             self.size * self.size_z * math.cos(math.radians(30)) + 2),
            (self.size * self.size_y +
             self.size * self.size_z * math.sin(math.radians(30)) + 2))

    def _generate_rect(self):
        offset_x = 0
        offset_y = self.size * self.size_z * math.sin(math.radians(30))
        angle = 30
        for z in range(self.size_z):
            for x in range(self.size_x):
                rec = self.create_rect(self.size,
                                       self.size,
                                       angle, 0, offset_x, offset_y)
                self._rect[(x, 0, z, 'xz')] = rec
                offset_x += self.size
            offset_y -= self.size * math.sin(math.radians(angle))
            offset_x = self.size * math.cos(math.radians(angle)) * (z + 1)

        offset_x = 0
        offset_y = (self.size * self.size_z * math.sin(math.radians(30)) +
                    self.size)
        angle = 90
        for y in range(self.size_y):
            for x in range(self.size_x):
                rec = self.create_rect(self.size,
                                       self.size,
                                       angle, 0, offset_x, offset_y)
                self._rect[(x, y, 0, 'xy')] = rec
                offset_x += self.size
            offset_y += self.size * math.sin(math.radians(angle))
            offset_x = 0

        offset_x = self.size_x * self.size
        offset_y = self.size * self.size_z * math.sin(math.radians(30))
        angle = 30
        for y in range(self.size_y):
            for z in range(self.size_z):
                rec = self.create_rect(self.size,
                                       self.size,
                                       angle, 90, offset_x, offset_y)
                self._rect[(self.size_x - 1, y, z, 'yz')] = rec
                offset_x += self.size * math.cos(math.radians(angle))
                offset_y -= self.size * math.sin(math.radians(angle))
            offset_y = (self.size * self.size_z * math.sin(math.radians(30)) +
                        self.size * (y + 1))
            offset_x = self.size_x * self.size

    def paintEvent(self, e):
        with temp_painter(self) as painter:
            painter.setPen(self.pen)
            painter.setBrush(self.brush)

            for i in self._rect:
                id_color = self._field[i[0]][i[1]][i[2]].color
                if id_color is not None:
                    color = BACK_COLORS[id_color % (len(BACK_COLORS) - 1)]
                else:
                    color = 0
                brush = QBrush(color)
                painter.setBrush(brush)
                painter.drawPolygon(self._rect[i])

                if self._field[i[0]][i[1]][i[2]].is_marked():
                    rect = self._rect[i].boundingRect()
                    painter.drawText(rect, Qt.AlignCenter,
                                     str(self._field[i[0]][i[1]][i[2]].mark))


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
        main_layout.addWidget(
            QLabel('Директория для сохранения\nголоволомки и её решения:'),
            5, 0)
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
            h = int(self.height.text()) if self.height.text() else 1
            d = int(self.depth.text()) if self.depth.text() else 1
        except ValueError:
            # TODO: Если некорректные параметры?
            return
        puzzle_name = self.path.text() + '\\'
        if self.puzzle_name.text():
            puzzle_name += self.puzzle_name.text()
        else:
            puzzle_name += 'shikaku_puzzle.txt'

        solution_name = self.path.text() + '\\'
        if self.solution_name.text():
            solution_name += self.solution_name.text()
        else:
            solution_name += 'shikaku_solution.txt'

        shikaku_generator.generate_puzzle(w, h, d, puzzle_name, solution_name)
        self.close()

    def _path_handler(self):
        path = QFileDialog.getExistingDirectory()
        self.path.setText(path)


class MainForm(QMainWindow):
    solver_signal = QtCore.pyqtSignal(object, object)

    def __init__(self):
        super().__init__()

        self.solver_signal.connect(self.signal_handler)

        self._task = None
        self._init_ui()

    def _init_ui(self):
        self.setMinimumSize(1200, 500)
        self.setGeometry(0, 0, 1200, 500)
        self.setWindowTitle('Shikaku')

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QVBoxLayout(centralWidget)

        self.progress_bar = QProgressBar(self)
        self.mainLayout.addWidget(self.progress_bar)
        self.progress_bar.setRange(0, 10000)

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
                task = Task.fromstr(data)
        except Exception as e:
            self.msg.setWindowTitle('Ошибка при открытии головоломки/решения:')
            if len(e.args) > 0:
                self.msg.setText(e.args[0])
            else:
                self.msg.setText('Что-то пошло не так...')
            self.msg.show()
        else:
            self._task = task
            self._update(task.field)
            self.progress_bar.setValue(0)

    def _clear_parallelepipeds(self):
        for p in self.parallelepipeds:
            p.close()
            self.grid.removeWidget(p)
        self.parallelepipeds.clear()

    def _update(self, field):
        self._deactivate_scrolls()

        self._clear_parallelepipeds()
        parallelepiped = GuiParallelepiped(field, self)
        self.parallelepipeds.append(parallelepiped)
        self.grid.addWidget(parallelepiped, 0, 0)

        self.scroll_x.setRange(0, self._task.size_x - 1)
        self.scroll_y.setRange(0, self._task.size_y - 1)
        self.scroll_z.setRange(0, self._task.size_z - 1)
        self.scroll_x.setValue(0)
        self.scroll_y.setValue(0)
        self.scroll_z.setValue(0)

        self._activate_scrolls()

    @thread
    def solver_handler(self, _):
        task = deepcopy(self._task)
        result = False
        if task:
            solver = Solver(task)
            self.progress_bar.setRange(0, solver.max + 1)
            self.progress_bar.setValue(solver.status)
            flag = True

            @thread
            def check_status():
                while flag:
                    self.progress_bar.setValue(solver.status)

            check_status()
            result = solver.solve()
            flag = False
        self.solver_signal.emit(result, task)

    def signal_handler(self, result, task):
        if not result:
            self.msg.setWindowTitle('Ошибка при решении головоломки')
            if task is None:
                self.msg.setText('Головоломка не обнаружена')
            else:
                self.msg.setText(
                    'Решатель не смог найти решение головоломки')
            self.msg.show()
        else:
            self._task = Task(field=task.solution,
                              solution=task.solution,
                              answer=task.answer)
            self._update(self._task.solution)

    def _scroll_handler(self):
        self._clear_parallelepipeds()

        dx = self.scroll_x.value()
        dy = self.scroll_y.value()
        dz = self.scroll_z.value()

        if not self._task.solution:
            field = self._task.field
        else:
            field = self._task.solution

        fields = [i for i in self._cut_task(field, dx, dy, dz)]
        if fields[1] is not None:
            parallelepiped = GuiParallelepiped(fields[1], self)
            self.parallelepipeds.append(parallelepiped)
            self.grid.addWidget(parallelepiped, 1, 0)

        if fields[0] is not None:
            parallelepiped = GuiParallelepiped(fields[0], self)
            self.parallelepipeds.append(parallelepiped)
            self.grid.addWidget(parallelepiped, 0, 0)

        if fields[3] is not None:
            parallelepiped = GuiParallelepiped(fields[3], self)
            self.parallelepipeds.append(parallelepiped)
            self.grid.addWidget(parallelepiped, 1, 1)

        if fields[2] is not None:
            parallelepiped = GuiParallelepiped(fields[2], self)
            self.parallelepipeds.append(parallelepiped)
            self.grid.addWidget(parallelepiped, 0, 1)

    @staticmethod
    def _cut_task(field, dx=0, dy=0, dz=0):
        def is_empty(arrays):
            if len(arrays) < 1:
                return True
            for array in arrays:
                if len(array) < 1:
                    return True
                for arr in array:
                    if len(arr) < 1:
                        return True
            return False

        field = deepcopy(field)
        for x in range(len(field)):  # Глубина
            for y in range(len(field[0])):
                field[x][y] = field[x][y][dz:]

        fields = [field[:dx], field[dx:]]

        for i in range(len(fields)):
            field = deepcopy(fields[i])
            for x in range(len(field)):
                field[x] = fields[i][x][:dy]

            yield None if is_empty(field) else field

            field = deepcopy(fields[i])
            for x in range(len(field)):
                field[x] = fields[i][x][dy:]

            yield None if is_empty(field) else field


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    sys.exit(app.exec_())
