import os
import unittest

from meshparser.exceptions import ParseError
from meshparser.vrmlparser.parser import VRMLParser
from meshparser.nodepare.pare import NodePare


file_path = os.path.dirname(os.path.realpath(__file__))


class ParserTestCase(unittest.TestCase):

    def testExistence(self):
        v = VRMLParser()
        self.assertRaises(IOError, v.parse, 'file that doesnt exist')

    def testParse1(self):
        v = VRMLParser()
        test_filename = os.path.join(file_path, 'data/Horse_1_1.wrl')
        self.assertTrue(v.canParse(test_filename))
        v.parse(test_filename)

    def testParse2(self):
        v = VRMLParser()
        v.parse(os.path.join(file_path, 'data/Horse_1_2.wrl'))
        self.assertEqual(0, len(v.getPoints()))

    def testParse3(self):
        v = VRMLParser()
        v.parse(os.path.join(file_path, 'data/Horse_1_3.wrl'))

        self.assertEqual(4572, len(v.getPoints()))
        self.assertEqual(9120, len(v.getElements()))

    def testOldFormat(self):
        v = VRMLParser()
        self.assertRaises(Exception, v.parse, os.path.join(file_path, 'data', 'old_format.wrl'))

    def testString(self):
        v = VRMLParser()
        test_file = os.path.join(file_path, 'data', 'string.wrl')
        v.parse(test_file)
        data = v._data
        self.assertIn('WorldInfo', data)
        self.assertIn('title', data['WorldInfo'])
        self.assertIn('info', data['WorldInfo'])
        self.assertEqual("\" hash # in a \\\"quoted # string\\\"\"", data["WorldInfo"]["title"])

    def testFStringSingle(self):
        from meshparser.vrmlparser.parser import _FString

        str1 = "\"A test string\""
        line_elements = str1.split()
        fs = _FString()
        fs.parse(line_elements)

        self.assertEqual("\"A test string\"", fs.getData())

    def testFStringMulti(self):
        from meshparser.vrmlparser.parser import _FString

        str1 = "[ \"Another test string\",\n      \"More testing string\" ]"
        line_elements = str1.split()
        fs = _FString()
        fs.parse(line_elements)

        string_data = fs.getData()
        self.assertEqual("\"Another test string\"", string_data[0])
        self.assertEqual("\"More testing string\"", string_data[1])

    def testFStringMultiSplit(self):
        from meshparser.vrmlparser.parser import _FString

        str1 = "[ \"Another test string\","
        str2 = "\"More testing string\" ]"
        line_elements_1 = str1.split()
        line_elements_2 = str2.split()
        fs = _FString()
        fs.parse(line_elements_1)
        self.assertFalse(fs.isFinished())
        fs.parse(line_elements_2)
        self.assertTrue(fs.isFinished())
        string_data = fs.getData()
        self.assertEqual("\"Another test string\"", string_data[0])
        self.assertEqual("\"More testing string\"", string_data[1])

    def testFVec3fSingle1(self):
        from meshparser.vrmlparser.parser import _FVec3f

        str1 = '0.176164 0.303858 0.144138'
        line_elements_1 = str1.split()

        fv = _FVec3f()
        fv.parse(line_elements_1)
        values = fv.getData()
        self.assertAlmostEquals(0.176164, values[0])
        self.assertAlmostEquals(0.303858, values[1])
        self.assertAlmostEquals(0.144138, values[2])

    def testFVec3fSingle2(self):
        from meshparser.vrmlparser.parser import _FVec3f

        str1 = '-1.67149e-08 -8.78133e-08  3.14159'
        line_elements_1 = str1.split()

        fv = _FVec3f()
        fv.parse(line_elements_1)
        values = fv.getData()
        self.assertAlmostEquals(-1.67149e-08, values[0])
        self.assertAlmostEquals(-8.78133e-08, values[1])
        self.assertAlmostEquals(3.14159, values[2])

        self.assertTrue(fv.isFinished())

    def testFNodeSimple(self):
        from meshparser.vrmlparser.parser import _FNode

        str1 = "Transform { }"
        line_elements_1 = str1.split()
        fn = _FNode()
        fn.parse(line_elements_1)
        values = fn.getData()
        self.assertIn('Transform', values)

    def testFNodeMulti(self):
        from meshparser.vrmlparser.parser import _FNode

        str1 = "[ Shape { appearance Appearance { material Material {  " \
               "ambientIntensity 0.2  diffuseColor 1.000 1.000 0.200 } } } ]"
        line_elements_1 = str1.split()
        fn = _FNode()
        fn.parse(line_elements_1)
        values = fn.getData()
        self.assertEqual(1, len(values))
        self.assertIn('Shape', values[0])

    def testInRange(self):
        from meshparser.vrmlparser.parser import _check_index_within_index_pairs
        self.assertTrue(_check_index_within_index_pairs(3, [[2, 4]]))
        self.assertTrue(_check_index_within_index_pairs(3, [[2, 4], [5, 8]]))
        self.assertFalse(_check_index_within_index_pairs(1, [[2, 4]]))
        self.assertFalse(_check_index_within_index_pairs(6, [[2, 4], [9, 15]]))

    def testComment(self):
        from meshparser.vrmlparser.parser import _remove_comment

        test_file = os.path.join(file_path, 'data', 'string.wrl')
        with open(test_file) as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                no_comment_line = _remove_comment(line.strip())
                if index == 4:
                    self.assertEqual("info [ \" # not a comment\" ]", no_comment_line)
                elif index == 5:
                    self.assertEqual("", no_comment_line)
                elif index == 7:
                    self.assertEqual("title \" hash # in a string\" ", no_comment_line)
                elif index == 8:
                    self.assertEqual("title \" hash # in a \\\"quoted # string\\\"\" ", no_comment_line)

    def testTransformBasic1(self):
        from meshparser.vrmlparser.parser import _TransformNode

        node = _TransformNode()
        test_file = os.path.join(file_path, 'data', 'transform_test_1.wrl')
        with open(test_file) as f:
            lines = f.readlines()
            while lines:
                line = lines.pop(0)
                line_elements = line.split()
                node.parse(line_elements)

            self.assertTrue(node.isFinished())
            self.assertIn('children', node._data)
            self.assertEqual(1, len(node._data['children']))

    def testTransformBasic2(self):
        from meshparser.vrmlparser.parser import _TransformNode

        node = _TransformNode()
        test_file = os.path.join(file_path, 'data', 'transform_test_2.wrl')
        with open(test_file) as f:
            lines = f.readlines()
            while lines:
                line = lines.pop(0)
                line_elements = line.split()
                node.parse(line_elements)

            self.assertTrue(node.isFinished())
            self.assertIn('children', node._data)
            self.assertEqual(1, len(node._data['children']))
            self.assertIn('Shape', node._data['children'][0])
            self.assertIn('appearance', node._data['children'][0]['Shape'])
            self.assertIn('Appearance', node._data['children'][0]['Shape']['appearance'])

    def testTransformBasic3(self):
        from meshparser.vrmlparser.parser import _TransformNode

        node = _TransformNode()
        test_file = os.path.join(file_path, 'data', 'transform_test_3.wrl')
        with open(test_file) as f:
            lines = f.readlines()
            while lines:
                line = lines.pop(0)
                line_elements = line.split()
                node.parse(line_elements)

            self.assertTrue(node.isFinished())
            self.assertIn('children', node._data)
            self.assertEqual(1, len(node._data['children']))
            self.assertIn('Shape', node._data['children'][0])
            self.assertIn('appearance', node._data['children'][0]['Shape'])
            self.assertIn('Appearance', node._data['children'][0]['Shape']['appearance'])
            self.assertIn('material', node._data['children'][0]['Shape']['appearance']['Appearance'])
            self.assertIn('Material', node._data['children'][0]['Shape']['appearance']['Appearance']['material'])
            self.assertIn('emissiveColor', node._data['children'][0]['Shape']['appearance']['Appearance']['material']['Material'])

    def testLab1(self):
        v = VRMLParser()
        test_file = os.path.join(file_path, 'data', 'lab1.wrl')
        self.assertRaises(ParseError, v.parse, test_file)

    def testDuplicatedPoints(self):
        v = VRMLParser()
        v.parse(os.path.join(file_path, 'data/Horse_1_4.wrl'))
        points = v.getPoints()
        self.assertEqual(33, len(points))
        np = NodePare()
        np.addPoints(points)
        np.parePoints()
        self.assertEqual(23, len(np.getParedPoints()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
