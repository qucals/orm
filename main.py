from orm import models
from orm.models import IntField, FloatField, TextField


class SomeTable(models.Model):
    pk = IntField(a_primary_key=True)
    some_field_1 = TextField()
    some_field_2 = IntField()
    some_field_3 = FloatField()

