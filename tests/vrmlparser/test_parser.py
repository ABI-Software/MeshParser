'''
Created on Jun 18, 2015

@author: hsorby
'''
import unittest

from meshparser.vrmlparser.parser import VRMLParser
from meshparser.nodepare.pare import NodePare


class ParserTestCase(unittest.TestCase):
    def testExistence(self):
        v = VRMLParser()
        self.assertRaises(IOError, v.parse, 'file that doesnt exist')

    def testParse1(self):
        v = VRMLParser()
        v.parse('data/Horse_1_1.wrl')

    def testParse2(self):
        v = VRMLParser()
        v.parse('data/Horse_1_2.wrl')

    def testParse3(self):
        v = VRMLParser()
        v.parse('data/Horse_1_3.wrl')

        self.assertEqual(4572, len(v.getPoints()))
        self.assertEqual(9120, len(v.getElements()))

    def testDuplicatedPoints(self):
        v = VRMLParser()
        v.parse('data/Horse_1_4.wrl')
        self.assertEqual(33, len(v.getPoints()))
        np = NodePare()
        np.addPoints(v.getPoints())
        np.parePoints()
        self.assertEqual(23, len(np.getParedPoints()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
