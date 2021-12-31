from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = 'FVH Feedback Map Admin'
    site_title = 'FVH Feedback Map Admin'
    site_url = None
