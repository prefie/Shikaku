from copy import deepcopy


class Task:
    def __init__(self, field):
        self.field = field
        self.solution = deepcopy(field)
        self.answer = []
        self.size_x, self.size_y, self.size_z =\
            len(field), len(field[0]), len(field[0][0])