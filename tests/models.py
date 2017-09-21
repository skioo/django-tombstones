import uuid

from django.db import models

from tombstones.models import SoftDeleteModel


class Person(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)


class Vehicle(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Person)
    make = models.CharField(max_length=100)
