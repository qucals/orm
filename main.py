from orm.models import *


class CustomTable(Model):
    pk = IntField(a_primary_key=True)
    float_field = FloatField()
    text_field = TextField()


class AnotherTable(Model):
    int_field = IntField()
    float_field = FloatField()


if __name__ == '__main__':
    CustomTable.objects.add(pk=1, float_field=3.1, text_field='test')
    CustomTable.objects.add(pk=2, float_field=3.2, text_field='foo')

    AnotherTable.objects.add(int_field=1, float_field=3.1)

    print(CustomTable.objects.filter(float_field__exact=3.1))
    print(CustomTable.objects.filter())