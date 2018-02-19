import os

from constants import TEMP_DIR

INTERESTING_FILE_TYPES = [".db", ".template", ".substitutions"]


def db_iterator(path):
    for root, _, files in os.walk(os.path.join(TEMP_DIR, path)):
        for f in files:
            p = os.path.join(root, f)
            if any(p.endswith(ext) for ext in INTERESTING_FILE_TYPES):
                yield os.path.relpath(p, start=os.path.join(TEMP_DIR, path))


def check_dbs(old, new):

    removed_dbs = []
    changed_dbs = []

    for db in db_iterator(old):
        if not os.path.exists(os.path.join(TEMP_DIR, new, db)):
            removed_dbs.append(db)
            continue

        with open(os.path.join(TEMP_DIR, old, db)) as old_file, open(os.path.join(TEMP_DIR, new, db)) as new_file:
            if old_file.readlines() != new_file.readlines():
                changed_dbs.append(db)

    return removed_dbs, changed_dbs
