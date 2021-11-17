import os.path
import sqlite3
import unittest

from orm import models
from orm.exceptions import IncorrectDatabaseFileName


class TestModel(unittest.TestCase):
    def tearDown(self):
        if os.path.exists('test_database.db'):
            os.remove('test_database.db')

    def test_database_creates_after_definition(self):
        """
        Тест: база данных создается после ее определения.
        """

        class TestTable(models.Model):
            _database_file = 'test_database.db'

        self.assertTrue(os.path.exists(TestTable._database_file))

        with sqlite3.connect(TestTable._database_file) as connection:
            cursor = connection.execute(
                f'SELECT name FROM sqlite_master WHERE type="table" AND name="{TestTable._table_name}"')
            self.assertEqual(1, len(cursor.fetchall()))

    def test_raise_incorrect_database_file_name(self):
        """
        Тест: вызывается исключение при некорректном задании имени
        """

        with self.assertRaises(IncorrectDatabaseFileName):
            class TestTable(models.Model):
                _database_file = None


if __name__ == '__main__':
    unittest.main()
