import difflib
import os

import shutil

from src.db_parser.common import parse_db_from_filepath, DbSyntaxError

INTERESTING_FILE_TYPES = [".db"]

DIRECTORIES_TO_ALWAYS_IGNORE = [
    ".git",
    "O.Common",
    "O.windows-x64",
    "bin",
    "lib",
    "include",
    ".project",
    "nicos-core",  # contains .template files that are not EPICS.
    "ad_kafka_interface",  # contains .template files that are not EPICS.
]

INTERESTING_DIRECTORIES = [
    os.path.join("EPICS", "ioc", "master"),
    os.path.join("EPICS", "ISIS"),
    os.path.join("EPICS", "support"),
]


class DbChangesIterator(object):

    def __init__(self, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path

    def dbs_in_old_path(self):
        for directory in INTERESTING_DIRECTORIES:
            for root, dirs, files in os.walk(os.path.join(self.old_path, directory)):
                dirs[:] = [d for d in dirs if d not in DIRECTORIES_TO_ALWAYS_IGNORE]
                for f in files:
                    p = os.path.join(root, f)
                    if any(p.endswith(ext) for ext in INTERESTING_FILE_TYPES):
                        yield os.path.relpath(p, start=self.old_path)

    def deleted_dbs(self):
        for db in self.dbs_in_old_path():
            if not os.path.exists(os.path.join(self.new_path, db)):
                yield db

    def modified_dbs(self):
        for db in self.dbs_in_old_path():
            if os.path.exists(os.path.join(self.new_path, db)):
                with open(os.path.join(self.old_path, db)) as old_file, \
                        open(os.path.join(self.new_path, db)) as new_file:
                    if old_file.readlines() != new_file.readlines():
                        yield db

    def change_descriptions(self):
        for db in self.modified_dbs():
            yield self._diff_dbs_by_path(db)

        for db in self.deleted_dbs():
            yield "A DB file was deleted from {}".format(db)

    def _diff_dbs_by_path(self, db_path):
        old_path = os.path.join(self.old_path, db_path)
        new_path = os.path.join(self.new_path, db_path)

        try:
            old_db = parse_db_from_filepath(old_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(old_path, e.__class__.__name__, e)

        try:
            new_db = parse_db_from_filepath(new_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(new_path, e.__class__.__name__, e)

        db_differences = self._diff_dbs(old_db, new_db)

        # If we can't generate a sensible diff from the parsed file, use difflib. May be whitespace changes or similar.
        if len(db_differences) > 0:
            return "DBs at '{}' and '{}' are different.\n  - {}"\
                .format(old_path, new_path, "\n  - ".join(db_differences))
        else:
            return "DBs at '{}' and '{}' are different, but previous API not changed".format(old_path, new_path)

    def _diff_dbs(self, old_db, new_db):
        """
        Finds differences between two DBs
        Returns:
            A list of strings describing the differences.
        """
        differences = []
        for old_rec in old_db:
            for r in new_db:
                if old_rec["name"] == r["name"]:
                    differences.extend(self._diff_records(old_rec, r))
                    break
            else:
                differences.append("Record removed: {}".format(old_rec["name"]))

        return differences

    def _diff_records(self, old_record, new_record):
        """
        Finds differences between two records
        Returns:
            A list of strings describing the differences.
        """
        differences = []
        for old_name, old_value in old_record["fields"]:
            for new_name, new_value in new_record["fields"]:
                if new_name == old_name:
                    if new_value != old_value:
                        differences.append("Field '{}' in record '{}' changed from '{}' to '{}'"
                                           .format(old_name, old_record["name"], old_value, new_value))
                    break
            else:
                differences.append("Field removed from record '{}': {}".format(old_record["name"], old_name))
        return differences
