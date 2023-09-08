import os
from pointpare import PointPare
import unittest

from meshparser.stlparser.parser import STLParser


file_path = os.path.dirname(os.path.realpath(__file__))


class ParserTestCase(unittest.TestCase):

    def testExistence(self):
        v = STLParser()
        self.assertRaises(IOError, v.parse, 'file that doesnt exist')
        
    def testParse1(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/ship.stl'))
        
        self.assertEqual(828, len(v.getElements())) 

    def testParse2(self):
        v = STLParser()
        test_filename = os.path.join(file_path, 'data/ship.zip')
        self.assertTrue(v.canParse(test_filename))
        v.parse(test_filename)

        self.assertEqual(828, len(v.getElements()))

    def testParse3(self):
        v = STLParser()
        test_filename = os.path.join(file_path, 'data/pelvis.stl')
        self.assertTrue(v.canParse(test_filename))
        v.parse(test_filename)

        self.assertEqual(52272, len(v.getElements())) 

    def testParse4(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis.zip'))

        self.assertEqual(52272, len(v.getElements())) 

    def testDuplicatedPoints(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/ship.stl'))
        self.assertEqual(2484, len(v.getPoints()))
        pp = PointPare()
        pp.add_points(v.getPoints())
        pp.pare_points()
        self.assertEqual(450, len(pp.get_pared_points()))

    def testZeroBased(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(33, len(v.getPoints()))
        elements = v.getElements(zero_based=False)
        self.assertEqual([4, 5, 6], elements[1])

    def testPared(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(13, len(v.getPoints(pared=True)))
        elements = v.getElements(pared=True)
        self.assertEqual([0, 3, 1], elements[1])

    def testParedZeroBased(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(33, len(v.getPoints()))
        elements = v.getElements(zero_based=False, pared=True)
        self.assertEqual([1, 4, 2], elements[1])

    # @unittest.skip("Skipping long test.")
    def testFailingModelInVersion000400(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/amazing_alveoli_minimal.stl'))
        self.assertEqual(310188, len(v.getPoints()))
        elements = v.getElements(zero_based=False, pared=True)
        self.assertEqual([4, 1, 3], elements[1])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
