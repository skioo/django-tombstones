from datetime import date

from django.db import IntegrityError
from django.test import TestCase
from pytest import raises

from .models import Car, Person, Vehicle, VicePrincipal


class SingleModelTest(TestCase):
    def test_it_should_hide_soft_deleted_objects(self):
        Person.objects.create(name='bob').soft_delete()
        assert Person.objects.count() == 0
        assert Person.all_including_deleted.count() == 1

    def test_it_should_raise_an_error_when_soft_deleting_twice(self):
        bob = Person.objects.create(name='bob')
        bob.soft_delete()
        assert Person.objects.count() == 0
        with raises(IntegrityError):
            bob.soft_delete()

    def test_it_should_allow_undeletion_of_objects(self):
        bob = Person.objects.create(name='bob')
        bob.soft_delete()
        assert Person.objects.count() == 0
        bob.soft_undelete()
        assert Person.objects.count() == 1

    def test_it_should_not_introduce_extra_sql_queries(self):
        Person.objects.create(name='alice')
        Person.objects.create(name='bob')
        Person.objects.create(name='charlie')
        Person.objects.create(name='dave').soft_delete()
        with self.assertNumQueries(1):
            assert Person.objects.count() == 3


class OneToManyRelationshipTest(TestCase):
    """
    In a one-to-many relationship soft-delete has an impact in one direction but not the other.
    """

    def setUp(self):
        bob = Person.objects.create(name='bob')
        Vehicle.objects.create(make='volvo', owner=bob)
        Vehicle.objects.create(make='trek', owner=bob)

    def test_it_should_hide_objects_on_the_many_side_of_the_relation(self):
        Vehicle.objects.get(make='volvo').soft_delete()
        bob = Person.objects.get(name='bob')
        assert bob.vehicles.count() == 1

    def test_it_cannot_hide_objects_on_the_one_side_of_the_relation(self):
        """
        If you are able to grab a reference to an object that has a foreign key to a soft-deleted object,
        that object stays accessible even though it was soft-deleted.
        """
        bob = Person.objects.get(name='bob')
        bob.soft_delete()
        volvo = Vehicle.objects.get(make='volvo')
        assert volvo.owner == bob


class OneToOneRelationshipTest(TestCase):
    """
    When two objects are in a one-to-one relationship, soft-deleting one has no impact on the other.
    """

    def setUp(self):
        bob = Person.objects.create(name='bob')
        volvo_vehicle = Vehicle.objects.create(make='volvo', owner=bob)
        Car.objects.create(vehicle=volvo_vehicle, license_plate='123456')

    def test_soft_deleting_the_car_doesnt_impact_the_vehicle(self):
        Car.objects.get(license_plate='123456').soft_delete()
        assert Car.objects.count() == 0
        assert Vehicle.objects.count() == 1
        assert Vehicle.objects.get(make='volvo').car.license_plate == '123456'

    def test_soft_deleting_the_vehicle_doesnt_impact_the_car(self):
        Vehicle.objects.get(make='volvo').soft_delete()
        assert Vehicle.objects.count() == 0
        assert Car.objects.count() == 1
        assert Car.objects.get(license_plate='123456').vehicle.make == 'volvo'


class SubclassTest(TestCase):
    def test_soft_deleting_as_subclass_does_not_affect_the_superclass(self):
        neal = VicePrincipal.objects.create(name='neal', hire_date=date(2017, 9, 23))
        neal.soft_delete()
        assert VicePrincipal.objects.count() == 0
        assert Person.objects.count() == 1
