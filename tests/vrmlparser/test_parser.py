'''
Created on Jun 18, 2015

@author: hsorby
'''
import unittest

from numptyparser.vrmlparser.parser import VRMLParser


class ParserTestCase(unittest.TestCase):


    def testExistence(self):
        v = VRMLParser()
        self.assertRaises(FileNotFoundError, v.parse, 'file that doesnt exist')
        
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
        self.assertEqual(36480, len(v.getElements()))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()