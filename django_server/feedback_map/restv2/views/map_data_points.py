from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from feedback_map import models
from feedback_map.rest.permissions import IsReviewerOrCreator, IsReviewer, user_is_reviewer
from feedback_map.rest.serializers import DictMapDataPointSerializer, MapDataPointSerializer, \
    MapDataPointCommentSerializer, MapDataPointCommentNotificationSerializer, TagSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = TagSerializer
    queryset = models.Tag.objects.filter(published__isnull=False).order_by('button_position')


class MapDataPointsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointSerializer
    queryset = models.MapDataPoint.objects.filter(visible=True)

    # Use simple serializer for list to improve performance:
    serializer_classes = {
        'list': DictMapDataPointSerializer
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # Fetch list as dicts rather than object instances for a bit more speed:
            return queryset.values()
        return queryset

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'hide_note']:
            return [IsReviewerOrCreator()]
        elif self.action in ['upvote', 'downvote']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'mark_processed':
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

    @action(methods=['PUT'], detail=True)
    def mark_processed(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.processed_by = request.user
        map_data_point.save()
        return Response('OK')

    @action(methods=['PUT'], detail=True)
    def hide_note(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.processed_by = request.user
        map_data_point.visible = False
        map_data_point.hidden_reason = request.data.get('hidden_reason', '')
        map_data_point.save()
        return Response('OK')

    @action(methods=['PUT'], detail=True)
    def upvote(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.upvotes.get_or_create(user=request.user)
        map_data_point.downvotes.filter(user=request.user).delete()
        map_data_point = self.get_object() # Reload from db
        serializer = self.get_serializer(map_data_point)
        return Response(serializer.data)

    @action(methods=['PUT'], detail=True)
    def downvote(self, request, *args, **kwargs):
        map_data_point = self.get_object()
        map_data_point.downvotes.get_or_create(user=request.user)
        map_data_point.upvotes.filter(user=request.user).delete()
        map_data_point = self.get_object() # Reload from db
        serializer = self.get_serializer(map_data_point)
        return Response(serializer.data)


class MapDataPointCommentsViewSet(viewsets.ModelViewSet):
    queryset = models.MapDataPointComment.objects.all().select_related('user')
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointCommentSerializer

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
    queryset = models.MapDataPointCommentNotification.objects\
        .filter(seen__isnull=True)\
        .select_related('comment__user')\
        .order_by('-id')
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataPointCommentNotificationSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset.none()
        return self.queryset.filter(user=self.request.user)

    @action(methods=['PUT'], detail=True)
    def mark_seen(self, request, *args, **kwargs):
        notification = self.get_object()
        if not notification.seen:
            notification.seen = timezone.now()
        notification.save()
        return Response('OK')


class MapDataPointsGeoJSON(ListAPIView):
    serializer_class = DictMapDataPointSerializer
    queryset = models.MapDataPoint.objects.filter(visible=True).values()
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [note['lon'], note['lat']]
                },
                "properties": serializer.to_representation(note)
            } for note in self.get_queryset()]
        })
