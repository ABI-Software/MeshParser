import unittest


class PackageTestCase(unittest.TestCase):

    def testVersion(self):
        import meshparser

        self.assertEqual('0.4.3', meshparser.__version__)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
