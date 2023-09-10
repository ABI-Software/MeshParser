import os
import unittest

from meshparser.vtkparser.parser import VTKParser


file_path = os.path.dirname(os.path.realpath(__file__))


class ParserTestCase(unittest.TestCase):

    def testExistence(self):
        v = VTKParser()
        self.assertRaises(IOError, v.parse, 'file that doesnt exist')

    def testParse1(self):
        v = VTKParser()
        test_filename = os.path.join(file_path, 'data/cardiac_jelly.vtk')
        self.assertTrue(v.can_parse(test_filename))
        v.parse(test_filename)

    def testParse2(self):
        v = VTKParser()
        v.parse(os.path.join(file_path, 'data/cardiac_jelly.vtk'))

        self.assertEqual(1170, len(v.get_points()))
        self.assertEqual(2314, len(v.get_elements()))

    def testOldFormat(self):
        v = VTKParser()
        test_filename = os.path.join(file_path, 'data/old_format.vtk')
        self.assertFalse(v.can_parse(test_filename))
        self.assertRaises(SyntaxError, v.parse, test_filename)

    def testBinaryFormat(self):
        v = VTKParser()
        self.assertRaises(NotImplementedError, v.parse, os.path.join(file_path, 'data/fake_binary_format.vtk'))


