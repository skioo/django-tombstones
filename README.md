django-tombstones
=================

[![Build Status](https://travis-ci.org/skioo/django-tombstones.svg?branch=master)](https://travis-ci.org/skioo/django-tombstones)


Adds soft-delete functionality to django.


Four design choices were made:

1) Does not change the behaviour of model.delete. Instead we add a soft_delete method to model instances.

2) Does not care about cascading. If there are models with relations, and you soft delete an object, the related objects are untouched.

3) The soft-deletion status of a model is stored in a generic Tombstones table, so each model is not cluttered with some extra 'deleted' attribute.
This means:
    * Making a model soft-deletable does not require database changes to that models table.
    * When using django-rest-framework model serializers, there is no need to worry about some 'deleted' attribute.
    * When querying soft-deletable models, an extra join to the tombstone table is made.

4) **Only works for models that have a primary key of type UUID**


Requirements
------------

* **Python**: 3.4 and over
* **Django**: Tested with django 1.11


Usage
-----

    INSTALLED_APPS = (
    ...
    'django.contrib.contenttypes',
    'tombstones.apps.TombstoneConfig',
    )


For every model where you want soft-delete, you should inherit from SoftDeleteModel:

    class MyModel(SoftDeleteModel):
        ...

Also use the soft-delete-aware ModelAdmin:

    class MyModelAdmin(SoftDeleteModelAdmin):
        actions = [soft_delete] # Shows the soft-delete this object action in the admin list
        list_filter = [SoftDeletedListFilter] # Displays a list filter on the right of the admin list
        list_display = [..., 'is_deleted'] # Displays a deleted column on the admin list
        ...



References
----------
- https://github.com/scoursen/django-softdelete was an inspiration


To work on this code
--------------------

    pip install -e .

To run tests:

    tox

To release a version to pypi:
- Edit \_\_version\_\_ in \_\_init\_\_.py
- Push and wait for the build to succeed
- Create a release in github, travis will build and deploy the new version to pypi: https://pypi.python.org/pypi/django-tombstones

