from random import randint, choice
from modules.task import Task
from modules.cube import Cube


class Generator:
    """Генератор головоломок Shikaku"""

    def __init__(self):
        """Создание генератора"""
        self._field = None
        self._solution = None
        self._answer = None

    def generate(self, dx, dy, dz):
        """По указанным измерениям генерирует поле и ответ"""
        if dx < 1 or dy < 1 or dz < 1:
            raise ValueError

        self._field = \
            [[[Cube() for _ in range(dz)] for _ in range(dy)] for _ in range(dx)]

        self._solution = \
            [[[Cube() for _ in range(dz)] for _ in range(dy)] for _ in range(dx)]
        self._answer = []
        for x in range(dx):
            for y in range(dy):
                for z in range(dz):
                    if self._solution[x][y][z].is_colored():
                        continue
                    sx = randint(1, dx - x)
                    sy = randint(1, dy - y)
                    sz = randint(1, dz - z)
                    while self._check_cells(x, y, z, sx, sy, sz):
                        sx = randint(1, dx - x)
                        sy = randint(1, dy - y)
                        sz = randint(1, dz - z)
                    self._generate_answer(x, y, z, sx, sy, sz)
        self._completion_volume()
        return (Task(self._field),
                Task(self._field, self._solution, self._answer))

    def _generate_answer(self, x, y, z, sx, sy, sz):
        """Заполняет solution цветами и answer - блоками"""
        block = []
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    self._solution[x + i][y + j][z + k].color = len(self._answer)
                    block.append([x + i, y + j, z + k])
        self._answer.append(block)

    def _completion_volume(self):
        """Заполняет поле объёмами и пустыми клетками"""
        for block in self._answer:
            v = len(block)
            x, y, z = choice(block)
            self._field[x][y][z].mark = v
            self._solution[x][y][z].mark = v

    def _check_cells(self, x, y, z, sx, sy, sz):
        """Возвращает True, если хотя бы одна клетка
        в параллелепипеде уже занята"""
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    if self._solution[x + i][y + j][z + k].is_colored():
                        return True
        return False
