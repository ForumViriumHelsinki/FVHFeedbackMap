from django.contrib.auth.models import User
from rest_framework import serializers

from feedback_map.rest.permissions import REVIEWER_GROUP


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class UserSerializer(serializers.ModelSerializer):
    is_reviewer = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'is_reviewer']

    def user_in_group(self, user, group_name):
        for group in user.groups.all():
            if group.name == group_name:
                return True
        return False

    def get_is_reviewer(self, user):
        return self.user_in_group(user, REVIEWER_GROUP)