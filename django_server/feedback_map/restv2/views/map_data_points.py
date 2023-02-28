import django_filters
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from feedback_map import models
from feedback_map.rest.permissions import (
    IsReviewerOrCreator,
    IsReviewer,
    user_is_reviewer,
)
from feedback_map.rest.serializers import (
    DictMapDataPointSerializer,
    MapDataPointSerializer,
    MapDataPointCommentSerializer,
    MapDataPointCommentNotificationSerializer,
    TagSerializer,
)


def create_polygon_or_fail(bbox: str) -> Polygon:
    """
    Create a Polygon from a bbox string. If the bbox string is invalid, raise ValidationError.
    """
    try:
        bbox = [float(x) for x in bbox.split(",")]
        if len(bbox) != 4:
            raise ValueError("Bbox must have 4 values (min_lon, min_lat, max_lon, max_lat)")
        if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            raise ValueError("Bbox must be in format (min_lon, min_lat, max_lon, max_lat)")
        return Polygon.from_bbox(bbox)
    except Exception as e:
        raise ValidationError("Invalid bbox: {}".format(e))


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class MapDataPointsFilter(django_filters.FilterSet):
    created_at = django_filters.IsoDateTimeFromToRangeFilter()
    modified_at = django_filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = models.MapDataPoint
        fields = ["created_at", "modified_at"]


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = TagSerializer
    pagination_class = StandardResultsSetPagination
    queryset = models.Tag.objects.filter(published__isnull=False).order_by("button_position")


class MapDataPointsViewSet(viewsets.ModelViewSet):
    """
    You can filter by:

    * `created_at_before`, `created_at_after`, `modified_at_before`, `modified_at_after`
       using ISO-formatted time strings.
    * bbox = left,bottom,right,top = min Longitude, min Latitude, max Longitude, max Latitude
    * coordinates+radius = lon,lat,radius

    You can order by

    * `[-]created_at`
    * `[-]modified_at`

    Note that there is not default ordering, but distance ordering is used if you use coordinates+radius filter.

    You can request max 1000 items per page using `page_size=1000` query parameter.

    Examples:

    * [?created_at_after=2023-01-01T00:00:00Z&ordering=created_at\
      ](?created_at_after=2023-01-01T00:00:00Z&ordering=created_at)
    * [?bbox=24.95,60.165,24.96,60.175&ordering=-created_at](?bbox=24.95,60.165,24.96,60.175&ordering=-created_at)
    * [?coordinates=60.166,24.951,1000](?coordinates=60.166,24.951,1000)
    * [?ordering=created_at](?ordering=created_at)
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MapDataPointsFilter
    ordering_fields = ["created_at", "modified_at"]
    # ordering = ["-created_at"]  # If default ordering is set, it is not possible to use ordering by distance
    queryset = models.MapDataPoint.objects.filter(visible=True)

    # Use simple serializer for list to improve performance:
    serializer_classes = {"list": DictMapDataPointSerializer}

    def get_queryset(self):
        """
        GIS filtering - note usage of geometry and geography fields.
        """
        queryset = super().get_queryset()
        bbox = self.request.query_params.get("bbox")
        if bbox:
            geom = create_polygon_or_fail(bbox)
            queryset = queryset.filter(geom__within=geom)
        coordinates = self.request.query_params.get("coordinates")
        if coordinates:
            lat, lon, radius = [float(x) for x in coordinates.split(",")]
            point = Point(lon, lat)
            queryset = queryset.filter(geog__distance_lt=(point, Distance(m=radius)))
            # Order queryset by distance
            queryset = queryset.annotate(distance=GeometryDistance("geog", point)).order_by("distance")
        if self.action == "list":
            # Fetch list as dicts rather than object instances for a bit more speed:
            return queryset.values()
        return queryset

    def get_permissions(self):
        if self.action in ["update", "partial_update", "hide_note"]:
            return [IsReviewerOrCreator()]
        elif self.action in ["upvote", "downvote"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "mark_processed":
            return [IsReviewer()]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def perform_create(self, serializer):
        map_data_point = serializer.save()
        if not self.request.user.is_anonymous:
            map_data_point.created_by = self.request.user
            map_data_point.modified_by = self.request.user
        map_data_point.save()

    def perform_update(self, serializer):
        map_data_point = serializer.save()
        if not self.request.user.is_anonymous:
            map_data_point.modified_by = self.request.user
        map_data_point.save()

    @action(methods=["PUT"], detail=True)
    def mark_processed(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.processed_by = request.user
        map_data_point.save()
        return Response("OK")

    @action(methods=["PUT"], detail=True)
    def hide_note(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.processed_by = request.user
        map_data_point.visible = False
        map_data_point.hidden_reason = request.data.get("hidden_reason", "")
        map_data_point.save()
        return Response("OK")

    @action(methods=["PUT"], detail=True)
    def upvote(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.upvotes.get_or_create(user=request.user)
        map_data_point.downvotes.filter(user=request.user).delete()
        map_data_point = self.get_object()  # Reload from db
        serializer = self.get_serializer(map_data_point)
        return Response(serializer.data)

    @action(methods=["PUT"], detail=True)
    def downvote(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.downvotes.get_or_create(user=request.user)
        map_data_point.upvotes.filter(user=request.user).delete()
        map_data_point = self.get_object()  # Reload from db
        serializer = self.get_serializer(map_data_point)
        return Response(serializer.data)


class MapDataPointCommentsViewSet(viewsets.ModelViewSet):
    queryset = models.MapDataPointComment.objects.all().select_related("user")
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointCommentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset.none()
        if user_is_reviewer(self.request.user):
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            comment = serializer.save()
        else:
            comment = serializer.save(user=self.request.user)
        comment.notify_users()
        return comment


class MapDataPointCommentNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.MapDataPointCommentNotification.objects.filter(seen__isnull=True)
        .select_related("comment__user")
        .order_by("-id")
    )
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointCommentNotificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset.none()
        return self.queryset.filter(user=self.request.user)

    @action(methods=["PUT"], detail=True)
    def mark_seen(self, request, *args, **kwargs):
        notification = self.get_object()
        if not notification.seen:
            notification.seen = timezone.now()
        notification.save()
        return Response("OK")


class MapDataPointsGeoJSON(ListAPIView):
    serializer_class = DictMapDataPointSerializer
    queryset = models.MapDataPoint.objects.filter(visible=True).values()
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [note["lon"], note["lat"]],
                        },
                        "properties": serializer.to_representation(note),
                    }
                    for note in self.get_queryset()
                ],
            }
        )
