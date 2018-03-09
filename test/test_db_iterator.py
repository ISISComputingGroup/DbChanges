import os
import unittest

from src.db_iterators import DbChangesIterator


class DbIteratorTests(unittest.TestCase):

    def setUp(self):
        self.db_change_iterator = DbChangesIterator(
            os.path.join(os.path.dirname(__file__), "test_data", "old"),
            os.path.join(os.path.dirname(__file__), "test_data", "new"),
        )

    def _emptyrecord(self, rec_type, name):
        return {
            "name": name,
            "type": rec_type,
            "fields": [],
            "infos": [],
            "aliases": [],
        }

    def test_GIVEN_two_equal_empty_records_WHEN_compared_THEN_no_differences_found(self):
        old_record = self._emptyrecord("ai", "$(P)HELLO")
        new_record = self._emptyrecord("ai", "$(P)HELLO")

        differences = self.db_change_iterator._diff_records(old_record, new_record)

        self.assertEqual(len(differences), 0)

    def test_GIVEN_field_is_removed_from_record_WHEN_compared_THEN_field_removed_message_in_differences(self):
        old_record = self._emptyrecord("ai", "$(P)HELLO")
        old_record["fields"].append(("VAL", "TEST_VALUE"))

        new_record = self._emptyrecord("ai", "$(P)HELLO")

        differences = self.db_change_iterator._diff_records(old_record, new_record)

        self.assertEqual(len(differences), 1)

        # Check that the record name and the field that was deleted is in the diff message
        self.assertIn("VAL", differences[0])
        self.assertIn("$(P)HELLO", differences[0])

    def test_WHEN_multiple_fields_are_removed_from_record_WHEN_compared_THEN_get_multiple_difference_messages(self):
        old_record = self._emptyrecord("ai", "$(P)HELLO")
        old_record["fields"].append(("VAL", "TEST_VALUE"))
        old_record["fields"].append(("PINI", "YES"))
        old_record["fields"].append(("SCAN", "1 second"))

        new_record = self._emptyrecord("ai", "$(P)HELLO")

        differences = self.db_change_iterator._diff_records(old_record, new_record)

        self.assertEqual(len(differences), 3)

    def test_WHEN_field_in_record_is_changed_WHEN_compared_THEN_field_changed_message_in_differences(self):
        old_record = self._emptyrecord("ai", "$(P)HELLO")
        old_record["fields"].append(("VAL", "TEST_VALUE"))

        new_record = self._emptyrecord("ai", "$(P)HELLO")
        new_record["fields"].append(("VAL", "NEW_TEST_VALUE"))

        differences = self.db_change_iterator._diff_records(old_record, new_record)

        self.assertEqual(len(differences), 1)

        # Check that the record name, the field that was changed, the old value and the new value are in the diff
        self.assertIn("VAL", differences[0])
        self.assertIn("$(P)HELLO", differences[0])
        self.assertIn("TEST_VALUE", differences[0])
        self.assertIn("NEW_TEST_VALUE", differences[0])

    def test_GIVEN_record_removed_from_db_WHEN_compare_dbs_THEN_record_removed_message_in_changes(self):

        differences = self.db_change_iterator._diff_dbs([self._emptyrecord("ai", "$(P)HELLO")], [])

        self.assertEqual(len(differences), 1)

        # Check that the record name is in the diff
        self.assertIn("$(P)HELLO", differences[0])
