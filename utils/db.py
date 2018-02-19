import os

from constants import TEMP_DIR


def db_iterator(path):
    for root, _, files in os.walk(os.path.join(TEMP_DIR, path)):
        for f in files:
            p = os.path.join(root, f)
            if p.endswith(".db"):
                yield os.path.relpath(p, start=os.path.join(TEMP_DIR, path))


def check_dbs(old, new):
    for db in db_iterator(old):
        if not os.path.exists(os.path.join(TEMP_DIR, new, db)):
            print("DB at {} now doesn't exist when it used to.".format(db))
            continue

        with open(os.path.join(TEMP_DIR, old, db)) as old_file, open(os.path.join(TEMP_DIR, new, db)) as new_file:
            if old_file.readlines() != new_file.readlines():
                print("File contents was different in DB {}".format(db))
