"""feedback_map URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from feedback_map import rest, restv2
from rest_framework.schemas import get_schema_view

schema_view_v1 = get_schema_view(
    title="FVH Feedback Map API v1",
    description="API v1 for interacting with packages in the FVH Feedback Map application",
    version="1.0.0", public=True)

schema_view_v2 = get_schema_view(
    title="FVH Feedback Map API v2",
    description="API v2 for interacting with packages in the FVH Feedback Map application",
    version="2.0.0", public=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest/', include(rest.urlpatterns)),  # TODO: redirect to /rest/v1/ first, then to /rest/v2/
    path('rest/v1/', include(rest.urlpatterns)),
    path('rest/v2/', include(restv2.urlpatterns)),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('openapi/', schema_view_v1, name='openapi-schema'),
    path('openapiv2/', schema_view_v2, name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
