import os

from src.db_parser.common import DbSyntaxError
from src.db_parser.lexer import Lexer
from src.db_parser.parser import Parser


class DbDiffer(object):
    def __init__(self, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path

    @staticmethod
    def parse_db_from_filepath(filepath):
        with open(filepath) as f:
            return Parser(Lexer(f.read())).db()

    def diff_dbs_by_path(self, db_path):
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
            old_db = DbDiffer.parse_db_from_filepath(old_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(
                old_path, e.__class__.__name__, e
            )

        try:
            new_db = DbDiffer.parse_db_from_filepath(new_path)
        except DbSyntaxError as e:
            return "Unable to parse db at {} because: {} {}".format(
                new_path, e.__class__.__name__, e
            )

        db_differences = self.diff_dbs(old_db, new_db)

        # If we can't generate a sensible diff from the parsed file, use difflib. May be whitespace changes or similar.
        if len(db_differences) > 0:
            return "DBs at '{}' and '{}' are different.\n  - {}".format(
                old_path, new_path, "\n  - ".join(db_differences)
            )
        else:
            return None  # API unchanged

    def diff_dbs(self, old_db, new_db):
        """
        Finds differences between two DBs
        Returns:
            A list of strings describing the differences.
        """
        differences = []
        for old_rec in old_db:
            for r in new_db:
                if (
                    old_rec["name"] == r["name"]
                ):  # Find a record in the new db with the same name as the old record.
                    differences.extend(self.diff_records(old_rec, r))
                    break
            else:  # Record with the same name was not found
                differences.append("Record removed: {}".format(old_rec["name"]))

        return differences

    def diff_records(self, old_record, new_record):
        """
        Finds differences between two records
        Returns:
            A list of strings describing the differences.
        """
        differences = []
        for old_name, old_value in old_record["fields"]:
            for new_name, new_value in new_record["fields"]:
                if (
                    new_name == old_name
                ):  # Find a field in the new record with the same name as the old field.
                    if new_value != old_value:
                        differences.append(
                            "Field '{}' in record '{}' changed from '{}' to '{}'".format(
                                old_name, old_record["name"], old_value, new_value
                            )
                        )
                    break
            else:  # Field with the same name not found
                differences.append(
                    "Field '{}' removed from '{}'".format(old_name, old_record["name"])
                )

        return differences
