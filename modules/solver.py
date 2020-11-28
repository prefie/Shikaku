from copy import deepcopy


class Solver:
    """Решатель головоломки Shikaku"""

    def __init__(self, task):
        self.task = task
        self.task.solution = deepcopy(self.task.field)
        self.task.answer = []
        self._blocks = self._completion_blocks()

    def solve(self, block_number=0):
        """Рекурсивно решает головоломку Shikaku"""
        if block_number >= len(self._blocks):
            return True

        block = self._blocks[block_number]
        for sides in block.sides:
            for i in range(sides[0]):
                for j in range(sides[1]):
                    for k in range(sides[2]):
                        if (sides[0] > self.task.size_x or
                                sides[1] > self.task.size_y or
                                sides[2] > self.task.size_z):
                            continue

                        point1 = Point(block.x + i - sides[0] + 1,
                                       block.y + j - sides[1] + 1,
                                       block.z - k)
                        point2 = Point(block.x + i,
                                       block.y + j,
                                       block.z - k + sides[2] - 1)

                        try:
                            parallelepiped = Parallelepiped(
                                point1, point2, block_number, block, self.task)
                        except ValueError:
                            continue

                        if not parallelepiped.is_conflict():
                            parallelepiped.fill_ids()

                            if self.solve(block_number + 1):
                                return True
                            else:
                                parallelepiped.clear_ids()
        return False

    def _completion_blocks(self):
        blocks = []
        for x in range(len(self.task.field)):
            for y in range(len(self.task.field[x])):
                for z in range(len(self.task.field[x][y])):
                    if self.task.field[x][y][z] != -1:
                        self.task.solution[x][y][z] = len(blocks)
                        blocks.append(
                            Block(x, y, z, self.task.field[x][y][z]))
        return blocks


class Block:
    """Блок фигуры в заданной точке с заданным объёмом"""
    def __init__(self, x, y, z, value):
        self.x = x
        self.y = y
        self.z = z
        self.value = value
        self.sides = self._calculate_sides()

    def _calculate_sides(self):
        """Возвращает всевозможные длины трёх измерений
        для указанного объёма"""
        sides = []
        for n in range(1, self.value + 1):
            if self.value % n != 0:
                continue
            area = self.value // n

            for j in range(1, area + 1):
                if area % j != 0:
                    continue
                sides.append((n, j, area // j))
        return sides


class Parallelepiped:
    """Параллелепипед"""
    def __init__(self, point1, point2, number_block, block, task):
        if not (0 <= point1.x <= point2.x < task.size_x and
                0 <= point1.y <= point2.y < task.size_y and
                0 <= point1.z <= point2.z < task.size_z):
            raise ValueError

        self.task = task
        self.point1 = point1
        self.point2 = point2
        self.block_number = number_block
        self.block = block

    def is_conflict(self):
        """Возвращает True, если существует конфликт с
        существующим параллелепипедом"""
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    if (self.task.solution[x][y][z] != -1 and
                            self.task.solution[x][y][z] != self.block_number):
                        return True
        return False

    def fill_ids(self):
        """Заполняет решение идентификатором параллелепипеда(номером блока)"""
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    self.task.solution[x][y][z] = self.block_number

        if self.block_number != -1:
            self._add_block_in_answer()

    def clear_ids(self):
        """Стирает идентификатор параллелепипеда с решения"""
        self.block_number = -1
        self.task.answer.pop(self.block_number)
        self.fill_ids()
        self.task.solution[self.block.x][self.block.y][self.block.z] =\
            self.block_number

    def _add_block_in_answer(self):
        """Добавляет указанный параллелепипед(блок) в ответ"""
        block = []
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    block.append([x, y, z])

        self.task.answer.append(block)


class Point:
    """Класс точки в трёхмерном пространстве"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y, self.z + point.z)

    def __sub__(self, point):
        return Point(self.x - point.x, self.y - point.y, self.z - point.z)
