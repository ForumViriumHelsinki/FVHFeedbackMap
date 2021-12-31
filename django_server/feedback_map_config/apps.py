from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    default_site = 'feedback_map_config.admin_site.AdminSite'
