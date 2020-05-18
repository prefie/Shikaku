from generator import Generator


class Solver:

    def __init__(self, task):
        self.task = task
        self.blocks = self._completion_blocks()

    def solve(self, block_number=0):
        if block_number >= len(self.blocks):
            return True

        block = self.blocks[block_number]
        # Перебираю все возможные длины сторон в блоке
        for sides in block.sides:
            for i in range(sides[0]):
                for j in range(sides[1]):
                    for k in range(sides[2]):
                        if (sides[0] > self.task.size_x or
                                sides[1] > self.task.size_y or
                                sides[2] > self.task.size_z):
                            continue
                        pos1 = Point(
                            block.x + i - sides[0] + 1,
                            block.y + j - sides[1] + 1,
                            block.z - k)
                        pos2 = Point(
                            block.x + i,
                            block.y + j,
                            block.z - k + sides[2] - 1)

                        try:
                            parallelepiped = Parallelepiped(
                                pos1, pos2, block_number, block, self.task)
                        except AssertionError:
                            continue

                        if not parallelepiped.check_conflicts():
                            parallelepiped.fill_ids()

                            if self.solve(block_number + 1):
                                return True

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
    def __init__(self, x, y, z, value):
        self.x = x
        self.y = y
        self.z = z
        self.value = value
        self.sides = self._calculate_sides()

    def _calculate_sides(self):
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
    def __init__(self, point1, point2, number_block, block, task):
        assert point1.z <= point2.z
        assert point1.y <= point2.y
        assert point1.x <= point2.x
        assert point2.z < task.size_z
        assert point2.y < task.size_y
        assert point2.x < task.size_x
        assert point1.x >= 0
        assert point1.y >= 0
        assert point1.z >= 0

        self.task = task
        self.pos1 = point1
        self.pos2 = point2
        self.block_number = number_block
        self.block = block

    def check_conflicts(self):
        for z in range(self.pos1.z, self.pos2.z + 1):
            for y in range(self.pos1.y, self.pos2.y + 1):
                for x in range(self.pos1.x, self.pos2.x + 1):
                    if (self.task.solution[x][y][z] != self.block_number and
                            self.task.solution[x][y][z] != -1):
                        return True
        return False

    def fill_ids(self):
        block = []
        for z in range(self.pos1.z, self.pos2.z + 1):
            for y in range(self.pos1.y, self.pos2.y + 1):
                for x in range(self.pos1.x, self.pos2.x + 1):
                    self.task.solution[x][y][z] = self.block_number
                    block.append([x, y, z])

        self.task.answer.append(block)

    def clear_ids(self):
        self.block_number = -1
        self.task.answer.pop(self.block_number)
        self.fill_ids()
        self.task.solution[self.block.x][self.block.y][self.block.z] =\
            self.block_number


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, point):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x + point.x, self.y + point.y, self.z + point.z)

    def __sub__(self, point):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x - point.x, self.y - point.y, self.z - point.z)

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z


g = Generator()
s = Solver(g.generate(5, 5, 5))
s.solve()

print()
print('Задача:')
for x in range(s.task.size_x):
    for y in range(s.task.size_y):
        print(s.task.field[x][y])
    print()

print()
print('Ответ:')
for x in range(s.task.size_x):
    for y in range(s.task.size_y):
        print(s.task.solution[x][y])
    print()

for i in range(0):
    s = Solver(g.generate(3, 3, 3))
    s.solve()

    print()
    print('Задача:')
    for x in range(s.task.size_x):
        for y in range(s.task.size_y):
            print(s.task.field[x][y])
        print()

    print()
    print('Ответ:')
    for x in range(s.task.size_x):
        for y in range(s.task.size_y):
            print(s.task.solution[x][y])
        print()

    for x in range(s.task.size_x):
        for y in range(s.task.size_y):
            for z in range(s.task.size_z):
                if s.task.solution[x][y][z] == -1:
                    raise Exception
