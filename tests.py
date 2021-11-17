import os.path
import sqlite3
import unittest

from orm import models
from orm.exceptions import IncorrectDatabaseFileName
from orm.models import IntField, TextField, FloatField

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

        TestTable.objects.add(2, 'another_text')
        self.assertEqual(2, len(TestTable.objects))

    def test_extract_data_from_table_by_filter(self):
        """
        Тест: получение данных из таблицы с помощью фильтрации
        """

        class TestTable(models.Model):
            id_column = IntField(a_primary_key=True)
            text_column = TextField()
            float_column = FloatField()

        TestTable.objects.add(1, 'text', 3.2)
        TestTable.objects.add(2, 'another_text_123_  ', 4.2)

        expected_first = [(1, 'text', 3.2)]
        extracted_first = TestTable.objects.filter(id_column__exact=1)
        self.assertEqual(expected_first, extracted_first)

        expected_second = [(2, 'another_text_123_  ', 4.2)]
        extracted_second = TestTable.objects.filter(text_column__exact='another_text_123_  ')
        self.assertEqual(expected_second, extracted_second)

        expected_third = [*expected_first, *extracted_second]
        extracted_third = TestTable.objects.filter()
        self.assertEqual(expected_third, extracted_third)

        expected_fourth = []
        extracted_fourth = TestTable.objects.filter(id_column__exact=3)
        self.assertEqual(expected_fourth, extracted_fourth)

        expected_fifth = [(1, 'text', 3.2)]
        extracted_fifth = TestTable.objects.filter(text_column__exact='text', float_column__exact=3.2)
        self.assertEqual(expected_first, extracted_fifth)


if __name__ == '__main__':
    unittest.main()
