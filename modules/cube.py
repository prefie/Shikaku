class Cube:
    def __init__(self, mark=None, color=None):
        self.mark = mark
        self.color = color

    def __str__(self):
        if self.color:
            return str(self.color)
        elif self.mark:
            return str(self.mark) + '*'
        else:
            return '-'

    def is_empty(self):
        return self.mark or self.color
