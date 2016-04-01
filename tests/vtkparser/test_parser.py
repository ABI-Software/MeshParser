import unittest

from meshparser.vtkparser.parser import VTKParser


class ParserTestCase(unittest.TestCase):

    def testExistence(self):
        v = VTKParser()
        self.assertRaises(IOError, v.parse, 'file that doesnt exist')

    def testParse1(self):
        v = VTKParser()
        v.parse('data/cardiac_jelly.vtk')

    def testParse2(self):
        v = VTKParser()
        v.parse('data/cardiac_jelly.vtk')

        self.assertEqual(1170, len(v.getPoints()))
        self.assertEqual(2314, len(v.getElements()))

