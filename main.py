from orm.models import *


class CustomTable(OrmModel):
    pk = OrmInteger(primary_key=True)
    some_field_1 = OrmText()
    some_field_2 = OrmInteger()
    some_field_3 = OrmFloat()


if __name__ == '__main__':
    table = CustomTable()
    table.add_entry(1, 'test', 3, 4.1)
    table.add_entry(2, '_test', 3, 1.1)

    print(table.objects())
    print(table.objects().filter(pk=2))
