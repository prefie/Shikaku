from random import randint, choice
from modules.task import Task


class Generator:
    """Генератор головоломок Shikaku"""
    def __init__(self):
        """Создание генератора"""
        self.field = None
        self.solution = None
        self.answer = None

    def generate(self, dx, dy, dz):
        """По указанным измерениям генерирует поле и ответ"""
        if dx < 1 or dy < 1 or dz < 1:
            raise ValueError

        self.field =\
            [[[-1 for _ in range(dz)] for _ in range(dy)] for _ in range(dx)]

        self.solution = \
            [[[-1 for _ in range(dz)] for _ in range(dy)] for _ in range(dx)]
        self.answer = []
        for x in range(dx):
            for y in range(dy):
                for z in range(dz):
                    if self.solution[x][y][z] != -1:
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
        return Task(self.field)

    def _generate_answer(self, x, y, z, sx, sy, sz):
        """Заполняет field цветами и answer - блоками"""
        block = []
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    self.solution[x + i][y + j][z + k] = len(self.answer)
                    block.append([x + i, y + j, z + k])
        self.answer.append(block)

    def _completion_volume(self):
        """Заполняет поле объёмами и пустыми клетками"""
        for block in self.answer:
            v = len(block)
            x, y, z = choice(block)
            self.field[x][y][z] = v

    def _check_cells(self, x, y, z, sx, sy, sz):
        """Возвращает True, если хотя бы одна клетка
        в параллелепипеде уже занята"""
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    if self.solution[x + i][y + j][z + k] != -1:
                        return True
        return False
