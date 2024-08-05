import os

from src.db_diff import DbDiffer

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
        self.differ = DbDiffer(old_path, new_path)

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
                with open(os.path.join(self.old_path, db)) as old_file, open(
                    os.path.join(self.new_path, db)
                ) as new_file:
                    if old_file.readlines() != new_file.readlines():
                        yield db

    def change_descriptions(self):
        """
        Generator that returns string descriptions of the changes for each database.

        This only returns changes where something *was* present in the API of the old database but is no longer present.
        It does not generate "changes" if functionality has only been added.
        """
        for db in self.modified_dbs():
            diff = self.differ.diff_dbs_by_path(db)
            if diff is not None:
                yield diff

        for db in self.deleted_dbs():
            yield "A DB file was deleted from {}".format(db)
