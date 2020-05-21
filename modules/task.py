from copy import deepcopy


class Task:
    """Класс задачи-головоломки Shikaku"""
    def __init__(self, field):
        self.field = field
        self.solution = None
        self.answer = []
        self.size_x, self.size_y, self.size_z =\
            len(field), len(field[0]), len(field[0][0])
