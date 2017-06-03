import os
import unittest

from meshparser.stlparser.parser import STLParser
from meshparser.nodepare.pare import NodePare


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
        v.parse(os.path.join(file_path, 'data/ship.zip'))

        self.assertEqual(828, len(v.getElements()))

    def testParse3(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis.stl'))

        self.assertEqual(52272, len(v.getElements())) 

    def testParse4(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis.zip'))

        self.assertEqual(52272, len(v.getElements())) 

    def testDuplicatedPoints(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/ship.stl'))
        self.assertEqual(2484, len(v.getPoints()))
        np = NodePare()
        np.addPoints(v.getPoints())
        np.parePoints()
        self.assertEqual(575, len(np.getParedPoints()))

    def testZeroBased(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(33, len(v.getPoints()))
        elements = v.getElements(zero_based=False)
        self.assertEquals([4, 5, 6], elements[1])

    def testPared(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(13, len(v.getPoints(pared=True)))
        elements = v.getElements(pared=True)
        self.assertEquals([0, 3, 1], elements[1])

    def testParedZeroBased(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/pelvis_minimal.stl'))
        self.assertEqual(33, len(v.getPoints()))
        elements = v.getElements(zero_based=False, pared=True)
        self.assertEquals([1, 4, 2], elements[1])

    def testFailingModelInVersion000400(self):
        v = STLParser()
        v.parse(os.path.join(file_path, 'data/amazing_alveoli_minimal.stl'))
        self.assertEqual(310188, len(v.getPoints()))
        elements = v.getElements(zero_based=False, pared=True)
        self.assertEquals([4, 1, 3], elements[1])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
