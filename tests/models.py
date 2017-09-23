import uuid

from django.db import models
from tombstones.models import SoftDeleteModel


class Person(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)


class VicePrincipal(Person):
    hire_date = models.DateField()


class Vehicle(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Person, related_name='vehicles')
    make = models.CharField(max_length=100)


class Car(SoftDeleteModel):
    vehicle = models.OneToOneField(Vehicle, primary_key=True)
    license_plate = models.CharField(max_length=6)
