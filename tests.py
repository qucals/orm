import os.path
import sqlite3
import unittest

from orm import models
from orm.exceptions import IncorrectDatabaseFileName
from orm.models import IntField, TextField

models.DEFAULT_DATABASE_NAME = 'test_database.db'


class TestModel(unittest.TestCase):
    def setUp(self):
        if os.path.exists(models.DEFAULT_DATABASE_NAME):
            os.remove(models.DEFAULT_DATABASE_NAME)

    def tearDown(self):
        if os.path.exists(models.DEFAULT_DATABASE_NAME):
            os.remove(models.DEFAULT_DATABASE_NAME)

    def test_database_creates_after_definition(self):
        """
        Тест: база данных создается после ее определения
        """

        class TestTable(models.Model):
            pass

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

    def test_adds_new_record_to_table(self):
        """
        Тест: добавляет новую запись в таблицу
        """

        class TestTable(models.Model):
            id_column = IntField(a_primary_key=True)
            text_column = TextField()

        TestTable.objects.add(1, 'text')
        self.assertEqual(1, len(TestTable.objects))


if __name__ == '__main__':
    unittest.main()
