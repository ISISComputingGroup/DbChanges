from __future__ import division

import argparse
import os
import sys

from src.constants import RELEASES_DIR
from src.db_iterators import DbChangesIterator


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="""Checks for changes in DB files between releases""")

    parser.add_argument("--old", required=True, type=str,
                        help="Name of the old release to compare against.")
    parser.add_argument("--new", required=True, type=str,
                        help="Name of the new release to compare.")

    args = parser.parse_args()

    # Filter to only include releases where we built an EPICS version (i.e. not client-only hotfixes)
    valid_releases = [p for p in os.listdir(RELEASES_DIR) if os.path.exists(os.path.join(RELEASES_DIR, p, "EPICS"))]

    if any(arg not in valid_releases for arg in (args.new, args.old)):
        print("Invalid release given. Valid releases are: {}".format(", ".join(valid_releases)))
        sys.exit(1)

    db_iterator = DbChangesIterator(os.path.join(RELEASES_DIR, args.old), os.path.join(RELEASES_DIR, args.new))

    for change in db_iterator.change_descriptions():
        print(change)
        print("\n-----\n")


if __name__ == "__main__":
    main()
