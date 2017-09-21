from django.db import models


class SoftDeleteManager(models.Manager):
    """ Hides the soft-deleted objects """

    def get_queryset(self):
        return super().get_queryset().filter(tombstones__isnull=True)
