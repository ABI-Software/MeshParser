import unittest

from meshparser.base.parser import BaseParser


class ParserTestCase(unittest.TestCase):

    def testCanParse(self):
        v = BaseParser()
        self.assertFalse(v.canParse('not-a-file'))

    def testParse(self):
        v = BaseParser()
        self.assertRaises(NotImplementedError, v.parse, 'not-a-file')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
