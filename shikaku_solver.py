#!/usr/bin/python3

import math
import sys
import threading
from copy import deepcopy
from modules.task import Task
from modules.solver import Solver
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QWidget,
                             QHBoxLayout, QFileDialog, QAction, QScrollBar,
                             QVBoxLayout, QGridLayout)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF

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
    11: QColor('white'),
    12: QColor('darkCyan'),
    13: QColor('darkBlue'),
    14: QColor('darkGreen'),
}


class GuiParallelepiped(QFrame):

    def __init__(self, task, cut_x1=None, cut_x2=None, parent=None):
        super().__init__(parent)
        self._task = deepcopy(task)

        if cut_x1 is not None and cut_x2 is not None:
            self._task.field = self._task.field[cut_x1:cut_x2 + 1]
            self._task.solution = self._task.solution[cut_x1:cut_x2 + 1]
            self._task.size_x = cut_x2 - cut_x1 + 1

        self.pen = QPen(QColor(0, 0, 0))
        self.pen.setWidth(3)
        self.brush = QBrush(QColor(255, 255, 0, 255))

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
            (50 * self._task.size_x +
             50 * self._task.size_z * math.cos(math.radians(30)) + 2),
            (50 * self._task.size_y +
             50 * self._task.size_z * math.sin(math.radians(30)) + 2))

    def _generate_rect(self):
        offset_x = 0
        offset_y = 50 * self._task.size_z * math.sin(math.radians(30))
        angle = 30
        for z in range(self._task.size_z):
            for x in range(self._task.size_x):
                rec = self.create_rect(50, 50, angle, 0, offset_x, offset_y)
                self._rect[(x, 0, z, 'xz')] = rec
                offset_x += 50
            offset_y -= 50 * math.sin(math.radians(angle))
            offset_x = 50 * math.cos(math.radians(angle)) * (z + 1)

        offset_x = 0
        offset_y = 50 * self._task.size_z * math.sin(math.radians(30)) + 50
        angle = 90
        for y in range(self._task.size_y):
            for x in range(self._task.size_x):
                rec = self.create_rect(50, 50, angle, 0, offset_x, offset_y)
                self._rect[(x, y, 0, 'xy')] = rec
                offset_x += 50
            offset_y += 50 * math.sin(math.radians(angle))
            offset_x = 0

        offset_x = self._task.size_x * 50
        offset_y = 50 * self._task.size_z * math.sin(math.radians(30))
        angle = 30
        for y in range(self._task.size_y):
            for z in range(self._task.size_z):
                rec = self.create_rect(50, 50, angle, 90, offset_x, offset_y)
                self._rect[(self._task.size_x - 1, y, z, 'yz')] = rec
                offset_x += 50 * math.cos(math.radians(angle))
                offset_y -= 50 * math.sin(math.radians(angle))
            offset_y = (50 * self._task.size_z * math.sin(math.radians(30)) +
                        50 * (y + 1))
            offset_x = self._task.size_x * 50

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


class MainForm(QMainWindow):
    solver_signal = QtCore.pyqtSignal(object, object)

    def __init__(self):
        super().__init__()

        self.solver_signal.connect(self._signal_handler)

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

        self.scroll_x = QScrollBar(Qt.Horizontal)
        self.mainLayout.addWidget(self.scroll_x)
        self.scroll_x.setRange(0, 0)
        self.scroll_z = QScrollBar()
        self.hBox.addWidget(self.scroll_z)
        self.scroll_z.setRange(0, 0)
        self.scroll_y = QScrollBar()
        self.scroll_y.setMinimum(1)
        self.scroll_y.setRange(1, 1)
        self.hBox.addWidget(self.scroll_y)

        self.scroll_x.valueChanged.connect(self.scroll_handle)
        self.scroll_y.valueChanged.connect(self.scroll_handle)
        self.scroll_z.valueChanged.connect(self.scroll_handle)

        newPuzzleAction = QAction('&Новая головоломка', self)
        newPuzzleAction.setShortcut('Ctrl+Q')
        newPuzzleAction.setStatusTip('Показать решение новой головоломки')
        newPuzzleAction.triggered.connect(self.showDialog)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Меню')
        fileMenu.addAction(newPuzzleAction)

        self.show()

    def showDialog(self):
        a = QFileDialog.getOpenFileName(self, 'Open file', '')
        filename = a[0]

        if filename:
            self._get_task(self.solver_signal, filename)

    @thread
    def _get_task(self, signal, filename):
        with open(filename, 'r') as f:
            data = f.read()
            field = parse_puzzle(data)
            s = Solver(Task(field))
            result = s.solve()
            signal.emit(result, s.task)

    def _signal_handler(self, result, task):
        if not result:
            return
            # raise ValueError
        self._task = task

        for p in self.parallelepipeds:
            p.close()
            self.grid.removeWidget(p)

        self.parallelepipeds.clear()

        self.scroll_x.setRange(0, self._task.size_x)
        self.scroll_y.setRange(1, self._task.size_y)
        self.scroll_z.setRange(0, self._task.size_z)
        self.scroll_y.setValue(self._task.size_y)

    def scroll_handle(self):
        for p in self.parallelepipeds:
            p.close()
            self.grid.removeWidget(p)
        self.parallelepipeds.clear()

        dx = self.scroll_x.value()
        dy = self.scroll_y.value()
        dz = self.scroll_z.value()

        tasks = [i for i in self.cut_task(self._task, dx, dy, dz)]
        if tasks[0] is not None:
            gui = GuiParallelepiped(tasks[0])
            self.parallelepipeds.append(gui)
            self.grid.addWidget(gui, 1, 0)
        if tasks[1] is not None:
            gui = GuiParallelepiped(tasks[1])
            self.parallelepipeds.append(gui)
            self.grid.addWidget(gui, 0, 0)
        if tasks[2] is not None:
            gui = GuiParallelepiped(tasks[2])
            self.parallelepipeds.append(gui)
            self.grid.addWidget(gui, 1, 1)
        if tasks[3] is not None:
            gui = GuiParallelepiped(tasks[3])
            self.parallelepipeds.append(gui)
            self.grid.addWidget(gui, 0, 1)

    def cut_task(self, task, dx=0, dy=0, dz=0):
        def is_empty(array):
            if not array:
                return True
            for x in array:
                for y in x:
                    if not y:
                        return True
            return False

        task = deepcopy(task)
        for x in range(len(task.field)):  # Глубина
            task.field[x] = task.field[x][:dy]
            task.solution[x] = task.solution[x][:dy]

        fields = [task.field[:dx], task.field[dx:]]
        solutions = [task.solution[:dx], task.solution[dx:]]

        for i in range(len(fields)):
            field = deepcopy(fields[i])
            solution = deepcopy(solutions[i])
            for x in range(len(field)):
                for y in range(len(field[x])):
                    field[x][y] = fields[i][x][y][:dz]
                    solution[x][y] = solutions[i][x][y][:dz]

            yield None if is_empty(field) else Task(field, solution)

            field = deepcopy(fields[i])
            solution = deepcopy(solutions[i])
            for x in range(len(field)):
                for y in range(len(field[x])):
                    field[x][y] = fields[i][x][y][dz:]
                    solution[x][y] = solutions[i][x][y][dz:]

            yield None if is_empty(field) else Task(field, solution)


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    sys.exit(app.exec_())
