import inspect
import sqlite3

#
# ORM FIELDS
#

class OrmField:
  __number_of_inheritances = 0

  def __init__(self, primary_key=False, not_null=True):
      self.__inheritance_number = OrmField.__number_of_inheritances + 1
      OrmField.__number_of_inheritances += 1

      self.is_primary_key = primary_key
      self.not_null = not_null

  def __str_create(self):
    text = ''
    if self.is_primary_key:
      text += ' PRIMARY KEY '
    if self.not_null:
      text += ' NOT NULL '
    return text

class OrmText(OrmField):
  def __str_create(self, column_name):
      return '{} text '.format(column_name) + super().__str_create()

class OrmInteger(OrmField):
  def __str_create(self, column_name):
      return '{} integer '.format(column_name) + super().__str_create()

class OrmFloat(OrmField):
  def __str_create(self, column_name):
      return '{} real '.format(column_name) + super().__str_create()

#
# ORM MODELS
#

class OrmModel:
  def __init__(self, db_file_name=None, db_table_name=None):
      db_file_name = (type(self).__name__+'.db') if db_file_name is None else db_file_name
      db_table_name = type(self).__name__ if db_table_name is None else db_table_name
      db_conn = self.__create_connection()

  def __create_connection(self):
    try:
        conn = sqlite3.connect(self.db_file)
        return conn
    except (Exception, ):
      return None

  def __create_table(self):
    fields = self.__get_all_table_fields()
    
    has_primary_key = False
    for (name_field, instance) in fields:
      if instance.is_primary_key:
        has_primary_key = True
        break
    
    if not has_primary_key:
      id_field = OrmInteger(primary_key=True)
      id_field_name = '_id_filed_{}_'.format(id_field.__inheritance_number)

      setattr(self, id_field_name, id_field)
      fields.insert(0, (id_field_name, id_field))

    sql_fields = []
    for idx, (name, instance) in enumerate(fields):
      _part = instance.__str_create(name)
      if idx != len(fields)-1:
        _part += ','
      sql_fields.append(_part)

    sqt_create_request = \
    """
    CREATE TABLE IF NOT EXISTS {} ({});
    """.format(self.db_table_name, ''.join(sql_fields))

  def __get_all_table_fields(self):
    attributes = [i for i in inspect.getmembers(self) if not inspect.ismethod(i[1])]
    
    fields = []
    for (name, instance) in attributes:
      if issubclass(type(instance), OrmField):
        fields.append((name, instance))
    
    return fields
