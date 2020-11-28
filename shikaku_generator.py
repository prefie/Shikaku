#!/usr/bin/python3

import argparse
import os
from modules.generator import Generator


def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(description='Shikaku generator')
    parser.add_argument('-H', '--height', type=int, required=True,
                        help='height of the Shikaku field')
    parser.add_argument('-W', '--width', type=int, required=True,
                        help='width of the Shikaku field')
    parser.add_argument('-D', '--depth', type=int, required=True,
                        help='depth of the Shikaku field')
    parser.add_argument('-P', '--puzzle', type=str,
                        default='shikaku_puzzle.txt',
                        help="save puzzle in file",
                        metavar='PATH')
    parser.add_argument('-S', '--solution', type=str,
                        default='shikaku_solution.txt',
                        help="save solution in file",
                        metavar='PATH')

    return parser.parse_args()


def save_in_file(filename, field):
    folder_path = os.path.dirname(filename)

    if folder_path != '' and not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(filename, 'w') as f:
        for i in range(len(field)):
            for j in range(len(field[i])):
                f.write(' '.join(map(
                    str,
                    map(lambda x: '-' if x == -1 else x, field[i][j]))))
                if j != len(field[i]) - 1:
                    f.write('\n')
            if i != len(field) - 1:
                f.write('\n\n')


def main():
    args = parse_args()
    generator = Generator()
    puzzle, solution = generator.generate(args.width, args.height, args.depth)
    save_in_file(args.puzzle, puzzle.field)
    save_in_file(args.solution, solution.solution)


if __name__ == '__main__':
    main()
