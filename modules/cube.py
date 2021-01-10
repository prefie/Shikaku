class Cube:
    def __init__(self, mark=None, color=None):
        self.mark = mark
        self.color = color

    def __str__(self):
        if self.is_painted() and self.is_marked():
            return str(self.color) + '_' + str(self.mark) + '*'
        elif self.is_painted():
            return str(self.color)
        elif self.is_marked():
            return str(self.mark) + '*'
        else:
            return '-'

    def is_painted(self):
        return self.color is not None

    def is_marked(self):
        return self.mark is not None
