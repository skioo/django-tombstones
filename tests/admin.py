from django.contrib import admin

from tombstones.admin import SoftDeleteModelAdmin
from .models import Person


@admin.register(Person)
class PersonAdmin(SoftDeleteModelAdmin):
    pass
