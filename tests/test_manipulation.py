import os
import unittest

from meshparser.parser import MeshParser
from meshparser.manipulation import calculate_centre_of_mass, translate, rotate

file_path = os.path.dirname(os.path.realpath(__file__))


class ManipulationTestCase(unittest.TestCase):

    def test_com_basic(self):
        mesh = {"points": [[0, 0, 0], [3, 0, 0], [0, 4, 0]], "elements": [[0, 1, 2]]}
        com = calculate_centre_of_mass(mesh)
        self.assertEqual([1.0, 1.3333333333333333, 0.0], com)

    def test_com(self):
        p = MeshParser()
        p.parse(os.path.join(file_path, "data/cylinder.stl"))

        points = p.get_points(True)
        self.assertEqual(40, len(points))

        mesh = {"points": points, "elements": p.get_elements(pared=True)}
        com = calculate_centre_of_mass(mesh)

        for i, val in enumerate([9.5, -2.5, 2.5]):
            self.assertAlmostEqual(val, com[i])

    def test_translate_basic(self):
        mesh = {"points": [[0, 0, 0], [3, 0, 0], [0, 4, 0]], "elements": [[0, 1, 2]]}

        translated_mesh = translate(mesh, [0.5, 0.5, 0])
        com = calculate_centre_of_mass(translated_mesh)
        for i, val in enumerate([1.5, 1.833333333333, 0]):
            self.assertAlmostEqual(val, com[i])

    def test_translate(self):
        p = MeshParser()
        p.parse(os.path.join(file_path, "data/cylinder.stl"))

        points = p.get_points(True)
        self.assertEqual(40, len(points))

        mesh = {"points": points, "elements": p.get_elements(pared=True)}
        translated_mesh = translate(mesh, [-9.5, 2.5, -2.5])
        com = calculate_centre_of_mass(translated_mesh)

        for i, val in enumerate([0, 0, 0]):
            self.assertAlmostEqual(val, com[i])

    def test_rotate_basic(self):
        mesh = {"points": [[0, 0, 0], [3, 0, 0], [0, 4, 0]], "elements": [[0, 1, 2]]}

        rotated_mesh = rotate(mesh, [0, 0, 1], 90)
        com = calculate_centre_of_mass(rotated_mesh)
        for i, val in enumerate([1.333333333333, -1, 0]):
            self.assertAlmostEqual(val, com[i])

    def test_rotate(self):
        p = MeshParser()
        p.parse(os.path.join(file_path, "data/cylinder.stl"))

        points = p.get_points(True)
        self.assertEqual(40, len(points))

        mesh = {"points": points, "elements": p.get_elements(pared=True)}
        translated_mesh = translate(mesh, [-9.5, 2.5, -2.5])
        rotated_mesh = rotate(translated_mesh, [-1, 0, 0], 90)
        com = calculate_centre_of_mass(rotated_mesh)

        for i, val in enumerate([0, 0, 0]):
            self.assertAlmostEqual(val, com[i])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
