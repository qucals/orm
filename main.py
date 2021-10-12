from orm.models import *

class CustomTable(Model):
    pk = IntField(a_primary_key=True)
    some_field = FloatField()


if __name__ == '__main__':
    # CustomTable.objects.filter(some_field='gfd')
    pass