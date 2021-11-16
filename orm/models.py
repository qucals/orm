import os.path
import sqlite3

from sqlite3 import Error

from orm.exceptions import DatabaseCreationError, IncorrectDatabaseFileName


class MetaModel(type):
    @staticmethod
    def _create_database(a_database_file):
        if type(a_database_file) is not str:
            raise IncorrectDatabaseFileName

        if not os.path.exists(a_database_file):
            try:
                _ = sqlite3.connect(a_database_file)
            except Error:
                raise DatabaseCreationError

    def _create_table(cls, a_database_file, a_table_name, a_attrs):
        pass

    def __new__(cls, name, bases, attrs):
        if '__no_user_class__' not in attrs:
            cls._create_database(attrs['_database_file'])
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=MetaModel):
    __no_user_class__ = True

    _database_file = 'database.db'
    _table_name = 'database'

