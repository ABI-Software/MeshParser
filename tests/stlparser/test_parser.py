import unittest

from meshparser.stlparser.parser import STLParser
from meshparser.nodepare.pare import NodePare


class ParserTestCase(unittest.TestCase):


    def testExistence(self):
        v = STLParser()
        self.assertRaises(FileNotFoundError, v.parse, 'file that doesnt exist')
        
    def testParse1(self):
        v = STLParser()
        v.parse('data/ship.stl')
        
        self.assertEqual(828, len(v.getElements())) 

    def testParse2(self):
        v = STLParser()
        v.parse('data/ship.zip')        

        self.assertEqual(828, len(v.getElements())) 

    def testParse3(self):
        v = STLParser()
        v.parse('data/pelvis.stl') 

        self.assertEqual(52272, len(v.getElements())) 

    def testParse4(self):
        v = STLParser()
        v.parse('data/pelvis.zip')        

        self.assertEqual(52272, len(v.getElements())) 

    def testDuplicatedPoints(self):
        v = STLParser()
        v.parse('data/ship.stl')
        self.assertEqual(2484, len(v.getPoints()))
        np = NodePare()
        np.addPoints(v.getPoints())
        np.parePoints()
        self.assertEqual(575, len(np.getParedPoints()))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()