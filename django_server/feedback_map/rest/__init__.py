from django.urls import path
from rest_framework import routers

from .views import (
    MapDataPointsViewSet, MapDataPointCommentsViewSet, MapDataPointsGeoJSON,
    MapDataPointCommentNotificationsViewSet,
    RecentMappersViewSet, TagsViewSet)

router = routers.DefaultRouter()
router.register('map_data_points', MapDataPointsViewSet)
router.register('map_data_point_comments', MapDataPointCommentsViewSet)
router.register('notifications', MapDataPointCommentNotificationsViewSet)
router.register('recent_mappers', RecentMappersViewSet)
router.register('tags', TagsViewSet)

urlpatterns = [
    path('map_data_points.geojson', MapDataPointsGeoJSON.as_view(), name='map_data_points_geojson')
] + router.urls
