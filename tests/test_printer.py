import os
import unittest

from meshparser.parser import MeshParser
from meshparser.manipulation import calculate_centre_of_mass, translate, rotate
from meshparser.printer import print_mesh

file_path = os.path.dirname(os.path.realpath(__file__))


class PrinterTestCase(unittest.TestCase):

    def test_print_basic(self):
        mesh = {"points": [[0, 0, 0], [3, 0, 0], [0, 4, 0]], "elements": [[0, 1, 2]]}

        translated_mesh = translate(mesh, [0.5, 0.5, 0])
        com = calculate_centre_of_mass(translated_mesh)
        for i, val in enumerate([1.5, 1.833333333333, 0]):
            self.assertAlmostEqual(val, com[i])

        filename = os.path.join(file_path, "data/translated_triangle.stl")
        print_mesh(translated_mesh, filename)

        self.assertTrue(filename)

        os.remove(filename)

    def test_print(self):
        p = MeshParser()
        p.parse(os.path.join(file_path, "data/cylinder.stl"))

        points = p.get_points(True)
        self.assertEqual(40, len(points))

        mesh = {"points": points, "elements": p.get_elements(pared=True)}
        translated_mesh = translate(mesh, [-9.5, 2.5, -2.5])
        rotated_mesh = rotate(translated_mesh, [-1, 0, 0], 90)
        shifted_mesh = translate(rotated_mesh, [0.75, 0, 0])

        filename = os.path.join(file_path, "data/transformed_cylinder.stl")
        print_mesh(shifted_mesh, filename)

        self.assertTrue(filename)

        os.remove(filename)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
