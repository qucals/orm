import os.path
import sqlite3


class BaseManager(list):
    def __init__(self, a_model_class, a_connection):
        self._model_class = a_model_class
        self._connection = a_connection
        self._table_name = self._model_class.__name__

    def filter(self, **kwargs):
        where_str = ''
        for field_name, field_value in kwargs.items():
            if field_name not in self._model_class.fields or \
                    type(field_value) != self._model_class.fields[field_name].get_type():
                raise ValueError
            else:
                where_str += '{}={}'


class MetaModel(type):
    __dbname__ = 'Database.db'

    manager_class = BaseManager

    @property
    def objects(cls):
        return cls._get_manager()

    def _get_manager(cls):
        return cls.manager_class(a_model_class=cls, a_connection=cls._connection)

    @staticmethod
    def _create_table(a_connection, a_table_name, fields):
        # noinspection PyProtectedMember
        sql_fields = [instance._str_create(name) for name, instance in fields.items()]
        sql_create_request = \
            """
            CREATE TABLE IF NOT EXISTS {} ({});
            """.format(a_table_name, ','.join(sql_fields))
        a_connection.execute(sql_create_request)

    def __new__(mcs, name, bases, attrs):
        if '__no_user_class__' in attrs:
            return super().__new__(mcs, name, bases, attrs)

        attrs['_table_name'] = name
        attrs['_connection'] = sqlite3.connect(mcs.__dbname__)

        field_attrs = {}
        for key, val in attrs.items():
            if not key.startswith('_') and isinstance(val, Field):
                field_attrs[key] = val

        has_primary_key = False
        for field in field_attrs.values():
            if field.is_primary_key():
                has_primary_key = True
                break

        if not has_primary_key:
            field_attrs['_primary_key_field'] = IntField(a_primary_key=True, a_autoincrement=True)
            attrs['_primary_key_field'] = field_attrs['_primary_key_field']

        mcs._create_table(attrs['_connection'], attrs['_table_name'], field_attrs)

        attrs['fields'] = field_attrs

        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=MetaModel):
    __no_user_class__ = ''


class Field(object):
    def __init__(self, a_primary_key=False, a_not_null=True, a_autoincrement=False):
        self._primary_key = a_primary_key
        self._not_null = a_not_null
        self._autoincrement = a_autoincrement

    def is_primary_key(self):
        return self._primary_key

    def get_type(self, *args, **kwargs):
        """
        Возвращает хранимый тип данных
        :rtype: Хранимый тип данных
        """

        return NotImplementedError()

    def _str_create(self, *args, **kwargs):
        """
        :rtype: Часть строки для запроса на создание SQLite
        """

        text = ''
        if self._primary_key:
            text += ' PRIMARY KEY '
        if self._not_null and not self._autoincrement:
            text += ' NOT NULL '
        if self._autoincrement:
            text += ' AUTOINCREMENT '
        return text


class IntField(Field):
    def get_type(self, *args, **kwargs):
        return int

    def _str_create(self, column_name):
        return '{} integer '.format(column_name) + super()._str_create()


class FloatField(Field):
    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(a_autoincrement=False, *args, **kwargs)

    def get_type(self, *args, **kwargs):
        return type(float)

    def _str_create(self, column_name):
        return '{} real '.format(column_name) + super()._str_create()


class TextField(Field):
    def __init__(self, *args, **kwargs):
        super(TextField, self).__init__(a_autoincrement=False, *args, **kwargs)

    def get_type(self, *args, **kwargs):
        return type(str)

    def _str_create(self, column_name):
        return '{} text '.format(column_name) + super()._str_create()
