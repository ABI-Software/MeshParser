import unittest

from meshparser.base.parser import BaseParser


class ParserTestCase(unittest.TestCase):

    def test_can_parse(self):
        v = BaseParser()
        self.assertFalse(v.can_parse('not-a-file'))

    def test_parse(self):
        v = BaseParser()
        self.assertRaises(NotImplementedError, v.parse, 'not-a-file')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
