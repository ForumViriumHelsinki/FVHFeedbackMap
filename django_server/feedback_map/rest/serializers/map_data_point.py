from django.conf import settings
from rest_framework import serializers

from feedback_map import models

from .base import BaseMapDataPointSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class MapDataPointCommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = models.MapDataPointComment
        fields = '__all__'


class MapDataPointCommentNotificationSerializer(serializers.ModelSerializer):
    comment = MapDataPointCommentSerializer(read_only=True)

    class Meta:
        model = models.MapDataPointCommentNotification
        fields = ['comment', 'id']


class DictMapDataPointSerializer(BaseMapDataPointSerializer):
    is_processed = serializers.BooleanField(read_only=True, source='processed_by_id')
    created_by = serializers.IntegerField(read_only=True, source='created_by_id')
    image = serializers.SerializerMethodField()

    false_default_fields = ['is_processed']

    class Meta:
        model = models.MapDataPoint
        fields = BaseMapDataPointSerializer.Meta.fields

    def to_representation(self, instance):
        result = super().to_representation(instance)
        for field in self.false_default_fields:
            result.setdefault(field, False)
        return result

    def get_image(self, note):
        return settings.MEDIA_URL + note['image'] if note.get('image', None) else None


class MapDataPointSerializer(BaseMapDataPointSerializer):
    # upvotes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='user_id')
    # downvotes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='user_id')
    comments = MapDataPointCommentSerializer(many=True, read_only=True)

    class Meta:
        model = models.MapDataPoint
        fields = ['id', 'comment', 'image', 'lat', 'lon', 'created_at',
                  'is_processed', 'tags', 'created_by', 'comments']  #, 'upvotes', 'downvotes']
