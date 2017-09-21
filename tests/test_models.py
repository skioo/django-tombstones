from django.db import IntegrityError
from django.test import TestCase
from pytest import raises

from .models import Person


class ModelTest(TestCase):
    def test_it_should_hide_soft_deleted_objects(self):
        bob = Person.objects.create(name='bob')
        assert len(Person.objects.all()) == 1

        bob.soft_delete()
        assert len(Person.objects.all()) == 0

        assert len(Person.all_including_deleted.all()) == 1

    def test_it_should_prevent_oft_deleting_twice(self):
        bob = Person.objects.create(name='bob')
        assert len(Person.objects.all()) == 1

        bob.soft_delete()
        assert len(Person.objects.all()) == 0

        with raises(IntegrityError):
            bob.soft_delete()
