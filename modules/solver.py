from copy import deepcopy


class Solver:
    """Решатель головоломки Shikaku"""

    def __init__(self, task):
        self.task = task
        self.task.solution = deepcopy(self.task.field)
        self.task.answer = []
        self._blocks = self._completion_blocks()
        self.depth = 0
        self.status = 0
        self.max = self._calculate_status()

    def solve(self, block_number=0):
        """Рекурсивно решает головоломку Shikaku"""
        if block_number >= len(self._blocks):
            return True

        block = self._blocks[block_number]

        for sides in block.sides:
            for i in range(sides[0]):
                for j in range(sides[1]):
                    for k in range(sides[2]):
                        if block_number <= self.depth:
                            self.status += 1

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
                                point1, point2, block, self.task)
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
        count = 0
        used_colors = set()
        for x in range(len(self.task.field)):
            for y in range(len(self.task.field[x])):
                for z in range(len(self.task.field[x][y])):
                    if self.task.field[x][y][z].is_marked():
                        count += 1
                        if not self.task.field[x][y][z].is_colored():
                            blocks.append(
                                Block(x, y, z, self.task.field[x][y][z].mark))
                        else:
                            used_colors.add(self.task.solution[x][y][z].color)

        colors = set(range(count)).difference(used_colors)

        for block in blocks:
            block.color = colors.pop()
            self.task.solution[block.x][block.y][block.z].color = block.color

        blocks.sort(key=lambda b: -b.value)

        return blocks

    def _calculate_status(self):
        if len(self._blocks) < 1:
            return 0

        count = self._blocks[0].value * len(self._blocks[0].sides)
        for i in range(1, len(self._blocks)):
            pred = count * self._blocks[i].value * len(self._blocks[i].sides)
            if pred > 10000:
                self.depth = i - 1
                return count
            count = pred

        self.depth = len(self._blocks) - 1
        return count


class Block:
    """Блок фигуры в заданной точке с заданным объёмом"""

    def __init__(self, x, y, z, value, color=None):
        self.x = x
        self.y = y
        self.z = z
        self.value = value
        self.color = color
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

    def __init__(self, point1, point2, block, task):
        if not (0 <= point1.x <= point2.x < task.size_x and
                0 <= point1.y <= point2.y < task.size_y and
                0 <= point1.z <= point2.z < task.size_z):
            raise ValueError

        self.task = task
        self.point1 = point1
        self.point2 = point2
        self.block = block

    def is_conflict(self):
        """Возвращает True, если существует конфликт с
        существующим параллелепипедом"""
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    if (self.task.solution[x][y][z].is_colored() and
                            self.task.solution[x][y][z].color !=
                            self.block.color):
                        return True
        return False

    def fill_ids(self):
        """Заполняет решение идентификатором параллелепипеда(цветом)"""
        self._fill_block(self.block.color)
        self._add_block_in_answer()

    def _fill_block(self, color):
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    self.task.solution[x][y][z].color = color

    def clear_ids(self):
        """Стирает идентификатор параллелепипеда с решения"""
        self._fill_block(None)
        self._remove_block_from_answer()
        self.task.solution[self.block.x][self.block.y][self.block.z].color = \
            self.block.color

    def _add_block_in_answer(self):
        """Добавляет указанный параллелепипед(блок) в ответ"""
        block = []
        for x in range(self.point1.x, self.point2.x + 1):
            for y in range(self.point1.y, self.point2.y + 1):
                for z in range(self.point1.z, self.point2.z + 1):
                    block.append([x, y, z])

        self.task.answer.append(block)

    def _remove_block_from_answer(self):
        self.task.answer.pop()


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
