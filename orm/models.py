import abc
import os.path
import sqlite3

from abc import ABC

from sqlite3 import Error

from orm.exceptions import DatabaseCreationError, IncorrectDatabaseFileName

DEFAULT_DATABASE_NAME = 'database.db'


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

    @staticmethod
    def _create_table(a_database_file, a_table_name, a_attrs):
        with sqlite3.connect(a_database_file) as connection:
            part_attrs_query = ''
            for idx, (name, inst) in enumerate(a_attrs.items()):
                part_attrs_query += f'\n{name} {inst.get_query_information()}'
                if idx + 1 != len(a_attrs):
                    part_attrs_query += ','
            query = f'CREATE TABLE IF NOT EXISTS {a_table_name}({part_attrs_query});'

            connection.execute(query)
            connection.commit()

    def __new__(mcs, name, bases, attrs):
        if '__no_user_class__' not in attrs:
            if '_database_file' not in attrs:
                attrs['_database_file'] = DEFAULT_DATABASE_NAME
            attrs['_table_name'] = name

            has_primary_key = False
            for value in attrs.values():
                if isinstance(value, INumericalField):
                    if value.primary_key:
                        has_primary_key = True
                        break

            if not has_primary_key:
                attrs['_id_field'] = IntField(a_primary_key=True, a_not_null=False, a_autoincrement=True)

            mcs._create_database(attrs['_database_file'])
            mcs._create_table(attrs['_database_file'],
                              attrs['_table_name'],
                              {attr: inst for attr, inst in attrs.items() if isinstance(inst, IField)})
        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=MetaModel):
    __no_user_class__ = True
    _database_file = 'database.db'


class IField:
    def __init__(self, a_primary_key=False, a_not_null=False):
        self._primary_key = a_primary_key
        self._not_null = a_not_null

    def get_query_information(self):
        return f'{self.get_type_in_sql_format()} {"PRIMARY KEY " if self.primary_key else ""}' \
               f'{"NOT NULL " if self.not_null else ""}'

    def get_type_in_sql_format(self):
        raise NotImplementedError

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def not_null(self):
        return self._not_null


class INumericalField(IField):
    def __init__(self, a_primary_key=False, a_not_null=False, a_autoincrement=False):
        super().__init__(a_primary_key=a_primary_key, a_not_null=a_not_null)
        self._autoincrement = a_autoincrement

    def get_query_information(self):
        return f'{super().get_query_information()}{"AUTOINCREMENT " if self.autoincrement else ""}'

    @property
    def autoincrement(self):
        return self._autoincrement


class IntField(INumericalField):
    def get_type_in_sql_format(self):
        return 'INTEGER'


class FloatField(INumericalField):
    def get_type_in_sql_format(self):
        return 'FLOAT'


class TextField(IField):
    def get_type_in_sql_format(self):
        return 'TEXT'
