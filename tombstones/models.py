from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .managers import SoftDeleteManager


class Tombstone(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField(db_index=True)
    content_object = GenericForeignKey()

    class Meta:
        unique_together = ['content_type', 'object_id']

    def __str__(self):
        # Requires an extra select to fetch the content object, so use sparingly
        return str(self.content_object)


def create_tombstone(obj):
    Tombstone.objects.create(content_object=obj)


class SoftDeleteModel(models.Model):
    """
     Replaces the default manager with one that hides soft-deleted objects.

     To access the soft-deleted objects, please use the all_including_deleted manager.
     """
    tombstones = GenericRelation(Tombstone)

    objects = SoftDeleteManager()
    all_including_deleted = models.Manager()

    class Meta:
        abstract = True

    def is_deleted(self):
        return self.tombstones.exists()

    is_deleted.boolean = True

    def soft_delete(self):
        create_tombstone(self)
