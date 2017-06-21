import os
import unittest

from meshparser.nodepare.pare import NodePare


class NodePareTestCase(unittest.TestCase):

    def testAddPoint(self):
        n = NodePare()
        n.addPoint([2, 5, 3])
        self.assertTrue(len(n._points) == 1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
