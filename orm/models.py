import inspect
import sqlite3

from typing import List, Dict


#
# ORM FIELDS
#

class OrmField:
    # Счетчик – общее количество наследований
    __number_of_inheritances = 0

    def __init__(self, primary_key=False, not_null=True, autoincrement=False, _no_inheritance=False):
        """
        :param primary_key: Индикатор, означающий, что данное поле является ключом
        :param not_null: Индикатор, означающий, что данное поле не может равнятся нулю
        :param autoincrement: Индикатор, означающий, что поле будет инкрементироваться
        :param _no_inheritance: Скрытое поле – индикатор, для того, чтобы не вносить данный класс в качестве наследуемого
        """

        if not _no_inheritance:
            self.__inheritance_number = OrmField.__number_of_inheritances + 1
            OrmField.__number_of_inheritances += 1
        else:
            self.__inheritance_number = 0

        self.is_primary_key = primary_key
        self.not_null = not_null
        self.autoincrement = autoincrement

    def get_stored_type(self, *args, **kwargs):
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
        if self.is_primary_key:
            text += ' PRIMARY KEY '
        if self.not_null and not self.autoincrement:
            text += ' NOT NULL '
        if self.autoincrement:
            text += ' AUTOINCREMENT '
        return text

    @property
    def inheritance_number(self):
        return self.__inheritance_number


class OrmText(OrmField):
    def __init__(self, *args, **kwargs):
        super(OrmText, self).__init__(autoincrement=False, *args, **kwargs)

    def get_stored_type(self, *args, **kwargs):
        return type(str)

    def _str_create(self, column_name):
        return '{} text '.format(column_name) + super()._str_create()


class OrmInteger(OrmField):
    def get_stored_type(self, *args, **kwargs):
        return type(int)

    def _str_create(self, column_name):
        return '{} integer '.format(column_name) + super()._str_create()


class OrmFloat(OrmField):
    def __init__(self, *args, **kwargs):
        super(OrmFloat, self).__init__(autoincrement=False, *args, **kwargs)

    def get_stored_type(self, *args, **kwargs):
        return type(float)

    def _str_create(self, column_name):
        return '{} real '.format(column_name) + super()._str_create()


#
# ORM MODELS
#

def check_connected(func):
    def wrapper(*args):
        if args[0].db_conn is None:
            raise ConnectionError()
        return func(*args)

    return wrapper


class ListOrm(list):
    def __init__(self, db_field_names, *args, **kwargs):
        super(ListOrm, self).__init__(args[0])
        self.db_field_names = db_field_names

    def filter(self, **kwargs):
        idx_fields = []
        for field_name in kwargs.keys():
            if field_name not in self.db_field_names:
                raise ValueError()
            idx_fields.append((self.db_field_names.index(field_name), kwargs[field_name]))

        filter_data = []
        for data in self.__iter__():
            need_add = True
            for field_idx, field_value in idx_fields:
                if data[field_idx] != field_value:
                    need_add = False
                    break
            if need_add:
                filter_data.append(data)
        return filter_data


class OrmModel:
    def __init__(self, db_file_name=None, db_table_name=None):
        self.db_file_name = (type(self).__name__ + '.db') if db_file_name is None else db_file_name
        self.db_table_name = type(self).__name__ if db_table_name is None else db_table_name
        self.db_fields = self.__get_all_table_fields()
        self.db_field_names = [name for (name, _) in self.db_fields]
        self.db_conn = self.__create_connection()

        self.__create_table()

    def __del__(self):
        if self.db_conn is not None:
            self.db_conn.close()

    @check_connected
    def add_entry(self, *args):
        # TODO: Можно реализовать эту функцию иначе для более простого использования по типу:
        # model.add_entry(pk=1, some_field_1='test', ...) – используя **kwargs

        auto_id_field_name = '_id_field_{}_'.format(self.db_fields[0][1].inheritance_number)
        has_auto_id_field = auto_id_field_name == self.db_fields[0][0]

        if has_auto_id_field:
            if len(args) != len(self.db_fields) - 1:
                raise AttributeError()
        else:
            if len(args) != len(self.db_fields):
                raise AttributeError()

        start_idx = 1 if has_auto_id_field else 0
        if self.__type_matching_test(data=list(args), start_idx=start_idx):
            raise TypeError()

        sql_values = ''
        for idx, a in enumerate(args):
            if type(a) is str:
                sql_values += '"{}"'.format(a)
            else:
                sql_values += str(a)
            if idx != len(args) - 1:
                sql_values += ', '

        sql_add_request = \
            """
            INSERT INTO {} ({})
            VALUES ({});
            """.format(self.db_table_name, ','.join(self.db_field_names), sql_values)

        self.db_conn.execute(sql_add_request)
        self.db_conn.commit()

    @check_connected
    def objects(self):
        sql_request = \
            """
            SELECT * FROM {}
            """.format(self.db_table_name)
        return ListOrm(self.db_field_names, self.db_conn.execute(sql_request).fetchall())

    def __type_matching_test(self, data: [List, Dict], start_idx: int = 0):
        if isinstance(data, list):
            for idx, d in enumerate(data):
                if type(d) != self.db_fields[idx + start_idx][1].get_stored_type():
                    return False
        return True

    def __create_connection(self):
        """
        Создает соединение с базой данных.

        :return: Соединение с базой данных в успешном случае, в ином None
        """

        try:
            conn = sqlite3.connect(self.db_file_name)
            return conn
        except (Exception,):
            return None

    @check_connected
    def __create_table(self):
        """
        Создает таблицу вместе со всеми полями класса
        """

        has_primary_key = False
        for (name_field, instance) in self.db_fields:
            if instance.is_primary_key:
                has_primary_key = True
                break

        if not has_primary_key:
            id_field = OrmInteger(primary_key=True, not_null=False, autoincrement=True)
            id_field_name = '_id_field_{}_'.format(id_field.inheritance_number)

            setattr(self, id_field_name, id_field)
            self.db_fields.insert(0, (id_field_name, id_field))

        sql_fields = [instance._str_create(name) for name, instance in self.db_fields]
        sql_create_request = \
            """
            CREATE TABLE IF NOT EXISTS {} ({});
            """.format(self.db_table_name, ','.join(sql_fields))

        self.db_conn.execute(sql_create_request)
        self.db_conn.commit()

    def __get_all_table_fields(self):
        """
        Собирает массив атрибутов данного класса

        :return: Массив атрибутов вида (name_attr, instance)
        """

        attributes = [i for i in inspect.getmembers(self) if not inspect.ismethod(i[1])]

        fields = []
        for (name, instance) in attributes:
            if issubclass(type(instance), OrmField):
                fields.append((name, instance))

        return fields
