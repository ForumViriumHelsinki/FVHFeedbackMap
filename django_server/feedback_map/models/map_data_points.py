from io import BytesIO

from PIL import Image as Img, UnidentifiedImageError, ExifTags
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.files import File
from django.db import models

from . import base
from .base import TimestampedModel


def upload_images_to(instance, filename):
    return f'map_data_points/{instance.id}/{filename}'


class Tag(models.Model):
    tag = models.CharField(max_length=64, primary_key=True, unique=True)
    color = models.CharField(max_length=32, choices=[(c, c) for c in ['primary', 'secondary', 'green', 'red']], default='primary')
    icon = models.FileField()
    published = models.DateTimeField(blank=True, null=True)


class MapDataPoint(TimestampedModel):
    lat = models.DecimalField(max_digits=11, decimal_places=8)
    lon = models.DecimalField(max_digits=11, decimal_places=8)
    image = models.ImageField(null=True, blank=True, upload_to=upload_images_to)
    comment = models.TextField(blank=True)
    tags = ArrayField(base_field=models.CharField(max_length=64), default=list, blank=True)

    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_notes')
    modified_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='modified_notes')

    processed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_notes')

    visible = models.BooleanField(default=True)
    hidden_reason = models.TextField(
        blank=True, help_text="If reviewer decides to hide the note, document reason here.")

    def __str__(self):
        return self.comment or super().__str__()

    def save(self, *args, **kwargs):
        if not self.image:
            return super().save(*args, **kwargs)

        try:
            pilImage = Img.open(BytesIO(self.image.read()))
        except (UnidentifiedImageError, FileNotFoundError):
            return super().save(*args, **kwargs)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = pilImage._getexif()  # noqa
        if not exif:
            return super().save(*args, **kwargs)

        exif = dict(exif.items())
        orientation = exif.get(orientation, None)
        if not orientation:
            return super().save(*args, **kwargs)

        if orientation == 3:
            pilImage = pilImage.rotate(180, expand=True)
        elif orientation == 6:
            pilImage = pilImage.rotate(270, expand=True)
        elif orientation == 8:
            pilImage = pilImage.rotate(90, expand=True)

        output = BytesIO()
        pilImage.save(output, format='JPEG', quality=75)
        output.seek(0)
        self.image = File(output, self.image.name)

        return super().save(*args, **kwargs)

    def is_processed(self):
        return bool(self.processed_by_id)

    def interested_users(self):
        from feedback_map.rest.permissions import REVIEWER_GROUP

        return User.objects.filter(
            models.Q(id__in=[self.created_by_id, self.modified_by_id, self.processed_by_id]) |
            models.Q(map_data_point_comments__map_data_point=self) |
            models.Q(groups__name=REVIEWER_GROUP)
        ).distinct()


class MapDataPointUpvote(base.Model):
    user = models.ForeignKey(User, related_name='map_data_point_upvotes', on_delete=models.CASCADE)
    map_data_point = models.ForeignKey(MapDataPoint, related_name='upvotes', on_delete=models.CASCADE)


class MapDataPointDownvote(base.Model):
    user = models.ForeignKey(User, related_name='map_data_point_downvotes', on_delete=models.CASCADE)
    map_data_point = models.ForeignKey(MapDataPoint, related_name='downvotes', on_delete=models.CASCADE)


class MapDataPointComment(base.Model):
    user = models.ForeignKey(User, related_name='map_data_point_comments', on_delete=models.CASCADE, null=True)
    map_data_point = models.ForeignKey(MapDataPoint, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    comment = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.comment or super().__str__()

    def notify_users(self):
        """
        Create MapDataPointCommentNotifications for users interested in this image note to notify them of the new
        comment
        """
        for user in self.map_data_point.interested_users():
            if user != self.user:
                self.notifications.create(user=user)


class MapDataPointCommentNotification(base.Model):
    comment = models.ForeignKey(MapDataPointComment, related_name='notifications', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    seen = models.DateTimeField(null=True, blank=True, db_index=True)
