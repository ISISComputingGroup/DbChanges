import os

from src.db_parser.common import DbSyntaxError
from src.db_parser.lexer import Lexer
from src.db_parser.parser import Parser

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
    """
    Contains iterators over DB files or differences between them.
    """

    def __init__(self, old_path, new_path):
        """
        Args:
            old_path: The path to the old release to be compared
            new_path: The path to the new release to be compared
        """
        self.old_path = old_path
        self.new_path = new_path

    @staticmethod
    def parse_db_from_filepath(filepath):
        with open(filepath) as f:
            return Parser(Lexer(f.read())).db()

    def dbs_in_old_path(self):
        """
        Generator that returns all the DB files in self.old_path/{INTERESTING_DIRECTORIES}
        """
        for directory in INTERESTING_DIRECTORIES:
            for root, dirs, files in os.walk(os.path.join(self.old_path, directory)):
                dirs[:] = [d for d in dirs if d not in DIRECTORIES_TO_ALWAYS_IGNORE]
                for f in files:
                    p = os.path.join(root, f)
                    if any(p.endswith(ext) for ext in INTERESTING_FILE_TYPES):
                        yield os.path.relpath(p, start=self.old_path)

    def deleted_dbs(self):
        """
        Generator that returns DBs that were removed from old_version to new_version
        """
        for db in self.dbs_in_old_path():
            if not os.path.exists(os.path.join(self.new_path, db)):
                yield db

    def modified_dbs(self):
        """
        Generator that returns DBs that were modified between old_version to new_version
        """
        for db in self.dbs_in_old_path():
            if os.path.exists(os.path.join(self.new_path, db)):
                with open(os.path.join(self.old_path, db)) as old_file, \
                        open(os.path.join(self.new_path, db)) as new_file:
                    if old_file.readlines() != new_file.readlines():
                        yield db

    def change_descriptions(self):
        """
        Generator that returns string descriptions of the changes for each database.

        This only returns changes where something *was* present in the API of the old database but is no longer present.
        It does not generate "changes" if functionality has only been added.
        """
        for db in self.modified_dbs():
            diff = self._diff_dbs_by_path(db)
            if diff is not None:
                yield self._diff_dbs_by_path(db)

        for db in self.deleted_dbs():
            yield "A DB file was deleted from {}".format(db)

    def _diff_dbs_by_path(self, db_path):
        """
        Finds the API differences between two DB files given a relative path.
        Args:
            db_path: The relative path from self.old_path or self.new_path to the DB file to diff.
        Returns:
            String describing the API differences, or None if there were no API differences.
        """
        old_path = os.path.join(self.old_path, db_path)
        new_path = os.path.join(self.new_path, db_path)

        try:
            old_db = DbChangesIterator.parse_db_from_filepath(old_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(old_path, e.__class__.__name__, e)

        try:
            new_db = DbChangesIterator.parse_db_from_filepath(new_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(new_path, e.__class__.__name__, e)

        db_differences = self._diff_dbs(old_db, new_db)

        # If we can't generate a sensible diff from the parsed file, use difflib. May be whitespace changes or similar.
        if len(db_differences) > 0:
            return "DBs at '{}' and '{}' are different.\n  - {}"\
                .format(old_path, new_path, "\n  - ".join(db_differences))
        else:
            return None  # API unchanged

    def _diff_dbs(self, old_db, new_db):
        """
        Finds differences between two DBs
        Returns:
            A list of strings describing the differences.
        """
        differences = []
        for old_rec in old_db:
            for r in new_db:
                if old_rec["name"] == r["name"]:  # Find a record in the new db with the same name as the old record.
                    differences.extend(self._diff_records(old_rec, r))
                    break
            else:  # Record with the same name was not found
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
                if new_name == old_name:  # Find a field in the new record with the same name as the old field.
                    if new_value != old_value:
                        differences.append("Field '{}' in record '{}' changed from '{}' to '{}'"
                                           .format(old_name, old_record["name"], old_value, new_value))
                    break
            else:  # Field with the same name not found
                differences.append("Field '{}' removed from '{}'".format(old_name, old_record["name"]))

        return differences
