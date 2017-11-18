from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import Tombstone


class SoftDeletedListFilter(admin.SimpleListFilter):
    """
    Hides soft-deleted objects by default. Also gives the option to show all objects, or just the deleted ones.
    """
    title = _('Soft deleted')

    parameter_name = 'soft-deleted'

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


def do_soft_delete(request, content_type_id, object_id):
    Tombstone.soft_delete(content_type_id, object_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def do_soft_undelete(request, content_type_id, object_id):
    Tombstone.soft_undelete(content_type_id, object_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SoftDeleteModelAdmin(admin.ModelAdmin):
    """
    The admin of soft-deletable models should inherit from this class.

    To display a list_filter that hides soft-deleted objects by default, and gives the option to reveal more
    you should include this list filter:

        list_filter = [SoftDeletedListFilter]

    To display a column in the admin with a button to delete-undelete each object, add this:

        list_display = [..., 'soft_delete_button']

    To display the same button, but in the admin detailed view, you should add a readonly field, like this:

        readonly_fields = [..., 'soft_delete_button']

    """
    list_filter = [SoftDeletedListFilter]
    readonly_fields = ['soft_delete_button']

    def get_queryset(self, request):
        qs = self.model.all_including_deleted.get_queryset() \
            .prefetch_related('tombstones')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_urls(self):
        custom_urls = [
            url(r'^(?P<content_type_id>.+)/(?P<object_id>.+)/soft_delete/$',
                self.admin_site.admin_view(do_soft_delete),
                name='tombstones-soft-delete'),
            url(r'^(?P<content_type_id>.+)/(?P<object_id>.+)/soft_undelete/$',
                self.admin_site.admin_view(do_soft_undelete),
                name='tombstones-soft-undelete')
        ]
        return custom_urls + super().get_urls()

    def soft_delete_button(self, obj):
        """
        Displays a button to delete/undelete the object, depending on its current status.
        """
        content_type = ContentType.objects.get_for_model(obj)
        if obj.is_deleted():
            return format_html(
                '<a class="button" href="{}">Undelete</a>',
                reverse('admin:tombstones-soft-undelete', args=[content_type.id, obj.pk]))
        else:
            return format_html(
                '<a class="button" href="{}">Delete</a>',
                reverse('admin:tombstones-soft-delete', args=[content_type.id, obj.pk]))

    soft_delete_button.short_description = _('Soft delete')


@admin.register(Tombstone)
class TombstoneAdmin(admin.ModelAdmin):
    """
    Even though tombstones are manipulated indirectly when each soft-deletable object is deleted/undeleted,
    we also want to let the administrator directly manipulate Tombstone objects.
    """
    date_hierarchy = 'created'
    list_display = ['created', 'link_to_soft_deleted_object']
    search_fields = ['object_id']
    list_filter = [('content_type', RelatedOnlyFieldListFilter)]
    readonly_fields = ['created']

    def link_to_soft_deleted_object(self, tombstone):
        text = '{}: {}'.format(tombstone.content_type.name, tombstone.object_id)
        url = reverse('admin:{}_{}_change'.format(
            tombstone.content_type.app_label,
            tombstone.content_type.model),
            args=(tombstone.object_id,))
        return format_html('<a href="{}">{}</a>', url, text)
