#!/usr/bin/env python3

import unittest
from modules.generator import Generator
from modules.solver import Solver
from modules.task import Task


class GeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = Generator()

    def test_generator_sides(self):
        task = self.generator.generate(1, 2, 3)
        self.assertEqual((1, 2, 3), (task.size_x, task.size_y, task.size_z))
        self.assertEqual(len(task.field), 1)
        self.assertEqual(len(task.field[0]), 2)
        self.assertEqual(len(task.field[0][0]), 3)

        task = self.generator.generate(5, 5, 5)
        self.assertEqual((5, 5, 5), (task.size_x, task.size_y, task.size_z))
        self.assertEqual(len(task.field), 5)
        self.assertEqual(len(task.field[0]), 5)
        self.assertEqual(len(task.field[0][0]), 5)

    def test_empty_generator(self):
        self.assertIsNone(self.generator.field)
        self.assertIsNone(self.generator.answer)

    def test_generator_number_cubes_in_answer(self):
        self.assertIsNone(self.generator.answer)
        task = self.generator.generate(2, 2, 2)
        count = 0
        for block in self.generator.answer:
            count += len(block)
        self.assertEqual(task.size_x * task.size_y * task.size_z, count, 8)

    def test_generator_number_blocks_in_answer(self):
        task = self.generator.generate(3, 3, 3)
        count = 0
        for x in range(task.size_x):
            for y in range(task.size_y):
                for z in range(task.size_z):
                    if task.field[x][y][z] != -1:
                        count += 1
        self.assertEqual(count, len(self.generator.answer))

    def test_bed_sides(self):
        with self.assertRaises(ValueError):
            self.generator.generate(-1, 2, 2)

        with self.assertRaises(ValueError):
            self.generator.generate(1, 0, 2)

        with self.assertRaises(ValueError):
            self.generator.generate(2, 2, -5)

    def test_sum_volume(self):
        task = self.generator.generate(3, 4, 3)
        volume = 0
        for x in range(task.size_x):
            for y in range(task.size_y):
                for z in range(task.size_z):
                    if task.field[x][y][z] != -1:
                        volume += task.field[x][y][z]
        self.assertEqual(task.size_x * task.size_y * task.size_z, volume)


class SolverTest(unittest.TestCase):

    def test_1(self):
        # (1, 2, 2)
        task = Task([[[-1, -1],
                      [-1, 4]]])
        solver = Solver(task)
        solver.solve()
        self.assertEqual(task.solution, [[[0, 0], [0, 0]]])

    def test_2(self):
        # (2, 2, 1)
        task = Task([[[-1], [-1]], [[-1], [4]]])
        solver = Solver(task)
        solver.solve()
        self.assertEqual(task.solution, [[[0], [0]], [[0], [0]]])


if __name__ == '__main__':
    unittest.main()
