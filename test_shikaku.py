#!/usr/bin/env python3

import unittest

from modules.cube import Cube
from modules.generator import Generator
from modules.solver import Solver
from modules.task import Task


class GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = Generator()

    def test_generator_sides(self):
        task, task_solution = self.generator.generate(1, 2, 3)
        self.assertEqual((1, 2, 3), (task.size_x, task.size_y, task.size_z))
        self.assertEqual(len(task.field), 1)
        self.assertEqual(len(task.field[0]), 2)
        self.assertEqual(len(task.field[0][0]), 3)

        task, task_solution = self.generator.generate(5, 5, 5)
        self.assertEqual((5, 5, 5), (task.size_x, task.size_y, task.size_z))
        self.assertEqual(len(task.field), 5)
        self.assertEqual(len(task.field[0]), 5)
        self.assertEqual(len(task.field[0][0]), 5)

    def test_empty_generator(self):
        self.assertIsNone(self.generator._field)
        self.assertIsNone(self.generator._solution)
        self.assertIsNone(self.generator._answer)

    def test_generator_number_cubes_in_answer(self):
        self.assertIsNone(self.generator._answer)
        task, task_solution = self.generator.generate(2, 2, 2)
        count = 0
        for block in self.generator._answer:
            count += len(block)
        self.assertEqual(task.size_x * task.size_y * task.size_z, count, 8)

        task, task_solution = self.generator.generate(3, 5, 6)
        count = 0
        for block in self.generator._answer:
            count += len(block)
        self.assertEqual(task.size_x * task.size_y * task.size_z, count, 90)

    def test_generator_number_blocks_in_answer(self):
        task, task_solution = self.generator.generate(3, 3, 3)
        count = 0
        for x in range(task.size_x):
            for y in range(task.size_y):
                for z in range(task.size_z):
                    if task.field[x][y][z].is_marked():
                        count += 1
        self.assertEqual(count, len(self.generator._answer))

    def test_bed_sides(self):
        with self.assertRaises(ValueError):
            self.generator.generate(-1, 2, 2)

        with self.assertRaises(ValueError):
            self.generator.generate(1, 0, 2)

        with self.assertRaises(ValueError):
            self.generator.generate(2, 2, -5)

        with self.assertRaises(TypeError):
            self.generator.generate(2, 2, 'a')

    def test_sum_volume(self):
        task1, _ = self.generator.generate(3, 4, 3)
        task2, _ = self.generator.generate(7, 5, 3)
        tasks = [task1, task2]
        for task in tasks:
            volume = 0
            for x in range(task.size_x):
                for y in range(task.size_y):
                    for z in range(task.size_z):
                        if task.field[x][y][z].is_marked():
                            volume += task.field[x][y][z].mark
            self.assertEqual(task.size_x * task.size_y * task.size_z, volume)

    def test_field_equality(self):
        task, task_solution = self.generator.generate(3, 4, 5)
        self.assertEqual(task.field, task_solution.field)

    def test_generated_solution(self):
        _, task_solution = self.generator.generate(3, 3, 3)
        for x in range(task_solution.size_x):
            for y in range(task_solution.size_y):
                for z in range(task_solution.size_z):
                    self.assertTrue(task_solution.solution[x][y][z].is_colored())


class TaskTest(unittest.TestCase):
    def test_save_and_load(self):
        task = Task([[[Cube(), Cube()],
                      [Cube(), Cube(mark=4)]]])

        task1 = Task([[[Cube(), Cube(mark=4)],
                      [Cube(), Cube()]],

                     [[Cube(mark=8), Cube()],
                      [Cube(), Cube()]],

                     [[Cube(), Cube()],
                      [Cube(), Cube()]]])

        task2 = Task([[[Cube(color=0, mark=2), Cube()],
                       [Cube(color=0), Cube(mark=2)]]])

        self.assertEqual(task, Task.fromstr(str(task)))
        self.assertEqual(task1, Task.fromstr(str(task1)))
        self.assertEqual(task2, Task.fromstr(str(task2)))

    def test_load_bad(self):
        with self.assertRaises(ValueError):
            Task.fromstr('asd')

        with self.assertRaises(ValueError):
            Task.fromstr('- -\n- - -')

        with self.assertRaises(ValueError):
            Task.fromstr('- 2*\n- -1')

    def test_init_bad(self):
        with self.assertRaises(ValueError):
            Task([])

        with self.assertRaises(ValueError):
            Task([[]])

        with self.assertRaises(ValueError):
            Task([[[]]])


class SolverTest(unittest.TestCase):
    def test_1(self):
        # (1, 2, 2)
        task = Task([[[Cube(), Cube()],
                      [Cube(), Cube(mark=4)]]])
        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[0][1][1].color,
                                range(1), range(task.size_y), range(task.size_z))

    def test_2(self):
        # (2, 2, 1)
        task = Task([[[Cube()], [Cube()]],

                     [[Cube(4)], [Cube()]]])
        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[1][0][0].color,
                                range(task.size_x), range(task.size_y), range(1))

    def test_3(self):
        # (2, 2, 2)
        task = Task([[[Cube(), Cube(mark=4)],
                      [Cube(), Cube()]],

                     [[Cube(), Cube(mark=4)],
                      [Cube(), Cube()]]])
        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)
        self.assertNotEqual(task.solution[0][0][1].color,
                            task.solution[1][0][1].color)

        self._check_color_range(task, task.solution[0][0][1].color,
                                range(1), range(task.size_y), range(task.size_z))

        self._check_color_range(task, task.solution[1][0][1].color,
                                range(1, 2), range(task.size_y), range(task.size_z))

    def test_4(self):
        # (2, 2, 2)
        task = Task([[[Cube(), Cube()],
                      [Cube(), Cube()]],

                     [[Cube(), Cube()],
                      [Cube(), Cube(mark=8)]]])
        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[1][1][1].color,
                                range(task.size_x), range(task.size_y), range(task.size_z))

    def test_5(self):
        # (3, 2, 2)
        task = Task([[[Cube(), Cube(mark=4)],
                      [Cube(), Cube()]],

                     [[Cube(mark=8), Cube()],
                      [Cube(), Cube()]],

                     [[Cube(), Cube()],
                      [Cube(), Cube()]]])
        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[0][0][1].color,
                                range(1), range(task.size_y), range(task.size_z))

        self._check_color_range(task, task.solution[1][0][0].color,
                                range(1, task.size_x), range(task.size_y), range(task.size_z))

    def test_6(self):
        # (3, 2, 3)
        task = Task([[[Cube(), Cube(), Cube()],
                      [Cube(), Cube(), Cube()]],

                     [[Cube(mark=6), Cube(mark=6), Cube()],
                      [Cube(), Cube(mark=6), Cube()]],

                     [[Cube(), Cube(), Cube()],
                      [Cube(), Cube(), Cube()]]])

        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[1][0][1].color,
                                range(task.size_x), range(1), range(1, task.size_z))

        self._check_color_range(task, task.solution[1][1][1].color,
                                range(task.size_x), range(1, task.size_y), range(1, task.size_z))

        self._check_color_range(task, task.solution[1][0][0].color,
                                range(task.size_x), range(task.size_y), range(1))

    def test_7(self):
        # (1, 3, 3) - частично решенная
        task = Task([[[Cube(), Cube(mark=2), Cube(mark=3, color=6)],
                      [Cube(mark=4), Cube(), Cube(color=6)],
                      [Cube(), Cube(), Cube(color=6)]]])

        solver = Solver(task)
        result = solver.solve()
        self.assertTrue(result)
        self._check_marks(task)

        self._check_color_range(task, task.solution[0][0][1].color,
                                range(task.size_x), range(1), range(2))

        self._check_color_range(task, task.solution[0][1][0].color,
                                range(task.size_x), range(1, task.size_y), range(2))

        self._check_color_range(task, task.solution[0][0][2].color,
                                range(task.size_x), range(task.size_y), range(2, task.size_z))

    def _check_color_range(self, task, value, range_x, range_y, range_z):
        for x in range_x:
            for y in range_y:
                for z in range_z:
                    self.assertEqual(value, task.solution[x][y][z].color)

    def _check_marks(self, task):
        for x in range(task.size_x):
            for y in range(task.size_y):
                for z in range(task.size_z):
                    self.assertEqual(task.field[x][y][z].mark, task.solution[x][y][z].mark)


if __name__ == '__main__':
    unittest.main()
