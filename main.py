from __future__ import division

import argparse
import os
import shutil
import stat
import sys
import six.moves

from utils.constants import TEMP_DIR, LOG
from utils.db import check_dbs
from utils.git_wrapper import clone_repos


def delete_temp_dir():

    def onerror(func, path, exc_info):
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            six.reraise(*exc_info)

    if os.path.exists(TEMP_DIR):
        LOG.info("Deleting temporary directory at {}".format(TEMP_DIR))
        shutil.rmtree(TEMP_DIR, onerror=onerror)
        LOG.info("Finished deleting temp directory at {}".format(TEMP_DIR))


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="""Checks for changes in DB files between releases""")

    parser.add_argument("--old", required=True, type=str,
                        help="Git branch name for the old release to compare against.")
    parser.add_argument("--new", required=True, type=str,
                        help="Git branch name for the new release to compare.")

    args = parser.parse_args()

    if args.old == args.new:
        print("Can't check for changes if old = new")
        sys.exit(1)

    try:
        clone_repos(TEMP_DIR, [args.old, args.new])
        six.moves.input("input")
        check_dbs(args.old, args.new)
    finally:
        if False:
            delete_temp_dir()


if __name__ == "__main__":
    main()
