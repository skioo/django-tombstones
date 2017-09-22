from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import Tombstone, create_tombstone


def link_to_object(ts):
    text = '{}: {}'.format(ts.content_type.name, ts.object_id)
    url = reverse('admin:{}_{}_change'.format(
        ts.content_type.app_label,
        ts.content_type.model),
        args=(ts.object_id,))
    return format_html('<a href="{}">{}</a>', url, text)


link_to_object.allow_tags = True
link_to_object.short_description = _('Soft deleted object')


@admin.register(Tombstone)
class TombstoneAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['created', link_to_object]
    search_fields = ['object_id']
    list_filter = [('content_type', RelatedOnlyFieldListFilter)]
    readonly_fields = ['created']


class SoftDeletedListFilter(admin.SimpleListFilter):
    title = _('deleted')

    parameter_name = 'deleted'

    def lookups(self, request, model_admin):
        return (
            (None, _('No')),
            ('yes', _('Yes')),
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(tombstones__isnull=True)

        if self.value() == 'yes':
            return queryset.filter(tombstones__isnull=False)

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }


def soft_delete(_modeladmin, _request, queryset):
    for o in queryset:
        create_tombstone(o)


soft_delete.short_description = _('Soft delete selected objects')


class SoftDeleteModelAdmin(admin.ModelAdmin):
    actions = [soft_delete]
    list_filter = [SoftDeletedListFilter]

    def get_queryset(self, request):
        qs = self.model.all_including_deleted.get_queryset().prefetch_related('tombstones')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
