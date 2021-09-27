from orm.models import *

class CustomTable(OrmModel):
  pk = OrmInteger(primary_key=True)
  some_field_1 = OrmText()
  some_field_2 = OrmInteger()
  some_field_3 = OrmFloat()