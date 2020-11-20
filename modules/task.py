class Task:
    """Класс задачи-головоломки Shikaku"""
    def __init__(self, field, solution=None, answer=None):
        self.field = field
        self.solution = solution
        self.answer = answer
        self.size_x, self.size_y, self.size_z =\
            len(field), len(field[0]), len(field[0][0])
