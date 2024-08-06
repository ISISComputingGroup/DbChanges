import os
import sys
import unittest

import xmlrunner

if __name__ == "__main__":
    suite = unittest.TestLoader().discover(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(0 if xmlrunner.XMLTestRunner(output="test-reports").run(suite).wasSuccessful() else 1)
