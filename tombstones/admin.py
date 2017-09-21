from django.contrib import admin

from .models import Tombstone, create_tombstone


@admin.register(Tombstone)
class TombstoneAdmin(admin.ModelAdmin):
    pass  # XXX


class SoftDeletedListFilter(admin.SimpleListFilter):
    title = 'deleted'

    parameter_name = 'deleted'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(tombstones__isnull=False)

        if self.value() == 'no':
            return queryset.filter(tombstones__isnull=True)


def soft_delete(modeladmin, request, queryset):
    for o in queryset:
        create_tombstone(o)


soft_delete.short_description = 'Soft delete selected objects'


class SoftDeleteModelAdmin(admin.ModelAdmin):
    actions = [soft_delete]
    list_filter = [SoftDeletedListFilter]

    def get_queryset(self, request):
        qs = self.model.all_including_deleted.get_queryset().prefetch_related('tombstones')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
