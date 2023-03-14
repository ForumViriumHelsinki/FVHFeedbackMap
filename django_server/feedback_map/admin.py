from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.conf import settings
from feedback_map import models


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('last_login', )


@admin.register(models.MapDataPoint)
class MapDataPointAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'image__', 'lat', 'lon', 'created_at', 'created_by', 'modified_at', 'modified_by',
                    'processed_by', 'visible']
    search_fields = ['comment']
    readonly_fields = ['image_', 'created_by', 'modified_by', 'processed_by']
    list_filter = ['visible', 'created_by', 'processed_by']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'modified_by', 'processed_by')

    def image_(self, map_data_point):
        if not map_data_point.image:
            return 'No image.'
        return mark_safe(f'<img src="{settings.MEDIA_URL}{map_data_point.image}" style="max-width: calc(100vw-260px); max-height: 60vh"/>')

    def image__(self, map_data_point):
        if not map_data_point.image:
            return 'No image.'
        return mark_safe(f'<a href="{settings.MEDIA_URL}{map_data_point.image}" target="_blank">image</a>')


@admin.register(models.MapDataPointComment)
class MapDataPointCommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'map_data_point', 'user', 'created_at']
    search_fields = ['comment']
    list_filter = ['user']
    date_hierarchy = 'created_at'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag', 'color', 'published', 'button_position']
    list_editable = ['color', 'published', 'button_position']
    list_filter = ['published']
