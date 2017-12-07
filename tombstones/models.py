from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Tombstone(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(db_index=True)
    content_object = GenericForeignKey()

    class Meta:
        unique_together = ['content_type', 'object_id']

    def __str__(self):
        # Requires an extra select to fetch the content object, so use sparingly
        return str(self.content_object)

    @staticmethod
    def soft_delete(content_type_id, object_id):
        Tombstone.objects.create(content_type_id=content_type_id, object_id=object_id)

    @staticmethod
    def soft_undelete(content_type_id, object_id):
        Tombstone.objects.filter(content_type_id=content_type_id, object_id=object_id).delete()


class HideSoftDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tombstones__isnull=True)


class SoftDeleteModel(models.Model):
    """
    Inherit from this class to enable soft-delete on your model.

    Requires the primary key of your model to be of type UUID.
    """
    tombstones = GenericRelation(Tombstone)

    objects = HideSoftDeletedManager()
    all_including_deleted = models.Manager()

    class Meta:
        abstract = True

    def is_deleted(self):
        return self.tombstones.exists()

    def soft_delete(self):
        Tombstone.objects.create(content_object=self)

    def soft_undelete(self):
        content_type = ContentType.objects.get_for_model(self)
        Tombstone.objects.filter(content_type=content_type, object_id=self.pk).delete()
