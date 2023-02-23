from collections import OrderedDict

from rest_framework import serializers

from feedback_map import models


class BaseMapDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapDataPoint
        fields = ['id', 'comment', 'image', 'lat', 'lon', 'is_processed',
                  'created_by', 'tags', 'created_at', 'modified_at']

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] not in [None, []]])