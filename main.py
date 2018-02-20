from __future__ import division

import argparse
import os
import sys

from constants import RELEASES_DIR
from db_iterators import DbIterator


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="""Checks for changes in DB files between releases""")

    parser.add_argument("--old", required=True, type=str,
                        help="Name of the old release to compare against.")
    parser.add_argument("--new", required=True, type=str,
                        help="Name of the new release to compare.")

    args = parser.parse_args()

    valid_releases = os.listdir(RELEASES_DIR)

    if any(arg not in valid_releases for arg in (args.new, args.old)):
        print("Invalid release given. Valid releases are: {}".format(", ".join(valid_releases)))
        sys.exit(1)

    db_iterator = DbIterator(os.path.join(RELEASES_DIR, args.old), os.path.join(RELEASES_DIR, args.new))

    for change in db_iterator.change_descriptions():
        print(change)


if __name__ == "__main__":
    main()
