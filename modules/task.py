from modules.cube import Cube


class Task:
    """Класс задачи-головоломки Shikaku"""
    def __init__(self, field, solution=None, answer=None):
        if self._field_is_empty(field):
            raise ValueError

        self.field = field
        self.solution = solution
        self.answer = answer
        self.size_x, self.size_y, self.size_z =\
            len(field), len(field[0]), len(field[0][0])

    @staticmethod
    def _field_is_empty(field):
        if len(field) < 1:
            return True
        for array in field:
            if len(array) < 1:
                return True
            for arr in array:
                if len(arr) < 1:
                    return True
        return False

    @staticmethod
    def fromstr(text):
        p_text = text.split('\n')
        field = [[]]

        dx = 0
        dy = 0
        for j in range(len(p_text)):
            string = p_text[j]
            if not string:
                dx += 1
                dy = 0
                field.append([])
                continue

            field[dx].append([])
            digit_str = ''
            color_with_mark = ''
            for i in range(len(string)):
                if (string[i] == '\t' or string[i] == ' ') and i != 0:
                    if len(digit_str) > 0:
                        field[dx][dy].append(Cube(color=int(digit_str)))
                        digit_str = ''
                    continue

                if string[i] == '-' and (i - 1 < 0 or string[i - 1] == '\t' or string[i - 1] == ' '):
                    if i + 1 < len(string) and string[i + 1] != '\t' and string[i + 1] != ' ':
                        raise ValueError(
                            f'строка:символ\n\n{j + 1}:{i + 2}\n{string}:{string[i + 1]}')
                    field[dx][dy].append(Cube())
                elif string[i].isdigit():
                    digit_str += string[i]

                elif string[i] == '*' and len(digit_str) > 0:
                    if len(color_with_mark) > 0:
                        field[dx][dy].append(Cube(color=int(color_with_mark), mark=int(digit_str)))
                        color_with_mark = ''
                        digit_str = ''
                        continue
                    if i + 1 < len(string) and string[i + 1] != '\t' and string[i + 1] != ' ':
                        raise ValueError(
                            f'строка:символ\n\n{j + 1}:{i + 2}\n{string}:{string[i + 1]}')
                    field[dx][dy].append(Cube(mark=int(digit_str)))
                    digit_str = ''

                elif string[i] == '_' and len(digit_str) > 0:
                    color_with_mark = digit_str
                    digit_str = ''

                else:
                    raise ValueError(
                        f'строка:символ\n\n{j + 1}:{i + 1}\n{string}:{string[i]}')

            if digit_str != '':
                field[dx][dy].append(Cube(color=int(digit_str)))

            dy += 1

        count_dy = len(field[0])
        count_dz = len(field[0][0])
        for x in range(len(field)):
            if len(field[x]) != count_dy:
                raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}')
            for y in range(len(field[x])):
                if len(field[x][y]) != count_dz:
                    raise ValueError(f'Нарушена целостность параллелепипеда: при x = {x}, y = {y}')

        return Task(field)

    def __str__(self):
        field = self.solution if self.solution else self.field
        answer = ''
        for i in range(len(field)):
            for j in range(len(field[i])):
                answer += ('\t'.join(map(str, field[i][j])))
                if j != len(field[i]) - 1:
                    answer += '\n'
            if i != len(field) - 1:
                answer += '\n\n'

        return answer

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False

        return self.field == other.field
