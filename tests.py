import os.path
import sqlite3
import unittest
from typing import Any

from orm import models
from orm.exceptions import IncorrectDatabaseFileName, DatabaseCreationError
from orm.models import MetaModel


class TestModel(unittest.TestCase):
    def tearDown(self):
        if os.path.exists('test_database.db'):
            os.remove('test_database.db')

    @staticmethod
    def create_database(a_database_file: Any = 'test_database.db'):
        class Table(models.Model):
            _database_file = a_database_file
        return Table

    def test_database_creates_after_definition(self):
        """
        Тест: база данных создается после ее определения.
        """

        Table = self.create_database()
        self.assertTrue(os.path.exists(Table._database_file))

    def test_raise_incorrect_database_file_name(self):
        """
        Тест: вызывается исключение при некорректном задании имени
        """

        with self.assertRaises(IncorrectDatabaseFileName):
            self.create_database(a_database_file=None)

    def test_create_table(self):
        """
        Тест: таблица в базе данных создается
        """

        Table = self.create_database()

        with sqlite3.connect(Table._database_file) as connection:
            cursor = connection.execute(
                f'SELECT name FROM sqlite_master WHERE type="table" AND name="{Table._table_name}"')
            self.assertEqual(1, len(cursor.fetchall()))


if __name__ == '__main__':
    unittest.main()
