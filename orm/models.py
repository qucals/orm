import enum
import os.path
import sqlite3
from abc import ABC

from sqlite3 import Error

from orm.exceptions import DatabaseCreationError, \
    IncorrectDatabaseFileName, IncorrectCountOfArguments, InvalidArgumentType, ArgumentNotFound, IncompatibleProperty

DEFAULT_DATABASE_NAME = 'database.db'


class BaseObjectsManager:
    class FilterSuffixType(str, enum.Enum):
        EXACT = 'exact'
        DEFAULT = ''

    def __init__(self, a_database_file, a_table_name, a_attrs):
        self._database_file = a_database_file
        self._table_name = a_table_name
        self._attrs = a_attrs

    def add(self, *args):
        if len(args) != len(self._attrs):
            raise IncorrectCountOfArguments

        query = f'INSERT INTO {self._table_name}('
        for idx, name in enumerate(self._attrs):
            query += f'{name}'
            if idx + 1 != len(self._attrs):
                query += ', '
        query += f') VALUES {self._format_query_values(args)}'

        with sqlite3.connect(self._database_file) as connection:
            connection.execute(query)
            connection.commit()

    def filter(self, **kwargs):
        filter_part_query = ''

        for name, value in kwargs.items():
            field_name, filter_type = name.split('__')

            if field_name not in self._attrs:
                raise ArgumentNotFound
            elif type(value) != self._attrs[field_name].get_stored_type():
                raise InvalidArgumentType

            filter_type = self._convert_to_filter_type(filter_type)
            filter_part_query = self._add_to_filter_query(filter_part_query, filter_type, field_name, value)

        query = f'SELECT * FROM {self._table_name}'

        if len(filter_part_query) > 0:
            query += f' WHERE {filter_part_query}'

        with sqlite3.connect(self._database_file) as connection:
            cursor = connection.execute(query)
            return cursor.fetchall()

    def _add_to_filter_query(self, a_query, a_type, a_name, a_value):
        if a_type == self.FilterSuffixType.DEFAULT:
            return

        if len(a_query) > 0:
            a_query += ' AND '

        if a_type == self.FilterSuffixType.EXACT:
            a_query += f'{a_name}="{a_value}"'

        return a_query

    def _convert_to_filter_type(self, a_str):
        try:
            return self.FilterSuffixType(a_str)
        except (Exception,):
            return self.FilterSuffixType.DEFAULT

    def _format_query_values(self, args):
        query_values = ''
        values = list(zip(args, self._attrs.values()))

        for idx, (arg, inst) in enumerate(values):
            if type(arg) != inst.get_stored_type():
                raise InvalidArgumentType
            else:
                query_values += f'"{arg}"'
                if idx + 1 != len(values):
                    query_values += ', '
        return f'({query_values})'

    def __len__(self):
        with sqlite3.connect(self._database_file) as connection:
            cursor = connection.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return cursor.fetchone()[0]


class MetaModel(type):
    objects_manager_class = BaseObjectsManager

    @property
    def objects(cls):
        return cls._get_objects_manager()

    def _get_objects_manager(cls):
        return cls.objects_manager_class(cls._database_file, cls._table_name, cls._table_fields)

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
            query = f'CREATE TABLE IF NOT EXISTS {a_table_name}({part_attrs_query})'

            connection.execute(query)
            connection.commit()

    def __new__(mcs, name, bases, attrs):
        if '__no_user_class__' not in attrs:
            if '_database_file' not in attrs:
                attrs['_database_file'] = DEFAULT_DATABASE_NAME
            attrs['_table_name'] = name

            attrs['_table_fields'] = {attr: inst for attr, inst in attrs.items() if isinstance(inst, IField)}

            has_primary_key = False
            for value in attrs.values():
                if isinstance(value, IIncrementalField):
                    if value.primary_key:
                        has_primary_key = True
                        break

            if not has_primary_key:
                attrs['_id_field'] = IntField(a_primary_key=True, a_not_null=False, a_autoincrement=True)

            mcs._create_database(attrs['_database_file'])
            mcs._create_table(attrs['_database_file'], attrs['_table_name'],
                              {attr: inst for attr, inst in attrs.items() if isinstance(inst, IField)})
        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=MetaModel):
    __no_user_class__ = True
    _database_file = DEFAULT_DATABASE_NAME
    _table_name = ''


class IField(ABC):
    def __init__(self, a_primary_key=False, a_not_null=False):
        self._primary_key = a_primary_key
        self._not_null = a_not_null

    def get_query_information(self):
        return f'{self.get_type_in_sql_format()} {"PRIMARY KEY " if self.primary_key else ""}' \
               f'{"NOT NULL " if self.not_null else ""}'

    def get_type_in_sql_format(self):
        raise NotImplementedError

    def get_stored_type(self):
        raise NotImplementedError

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def not_null(self):
        return self._not_null


class IIncrementalField(IField, ABC):
    def __init__(self, a_primary_key=False, a_not_null=False, a_autoincrement=False):
        super().__init__(a_primary_key=a_primary_key, a_not_null=a_not_null)
        self._autoincrement = a_autoincrement

        if self.not_null and self.autoincrement:
            raise IncompatibleProperty

    def get_query_information(self):
        return f'{super().get_query_information()}{"AUTOINCREMENT " if self.autoincrement else ""}'

    @property
    def autoincrement(self):
        return self._autoincrement


class IntField(IIncrementalField):
    def get_type_in_sql_format(self):
        return 'INTEGER'

    def get_stored_type(self):
        return int


class FloatField(IField):
    def get_type_in_sql_format(self):
        return 'FLOAT'

    def get_stored_type(self):
        return float


class TextField(IField):
    def get_type_in_sql_format(self):
        return 'TEXT'

    def get_stored_type(self):
        return str
