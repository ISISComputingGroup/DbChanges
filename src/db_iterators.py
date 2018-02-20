import os

from src.db_parser.common import parse_db_from_filepath


class DbIterator(object):
    INTERESTING_FILE_TYPES = [".db", ".template"]

    def __init__(self, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path

    def dbs_in_old_path(self):
        for root, _, files in os.walk(self.old_path):
            for f in files:
                p = os.path.join(root, f)
                if any(p.endswith(ext) for ext in self.INTERESTING_FILE_TYPES):
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
                        print("Parsing {}".format(os.path.join(self.old_path, db)))
                        db = parse_db_from_filepath(os.path.join(self.old_path, db))
                        print(db)
                        yield db

    def change_descriptions(self):
        for db in self.modified_dbs():
            yield "A DB file was modified at {}. Changes:\n    {}"\
                .format(db, "\n    ".join(self.change_details(db)))

        for db in self.deleted_dbs():
            yield "A DB file was deleted from {}".format(db)

    def change_details(self, rec):
        return ["record blah removed", "record blah added", "record blah2 added"]
