import os
import unittest

from xmlrunner import xmlrunner


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(os.path.abspath(__file__)))
    xmlrunner.XMLTestRunner(output="test-reports").run(suite)


if __name__ == "__main__":
    main()
