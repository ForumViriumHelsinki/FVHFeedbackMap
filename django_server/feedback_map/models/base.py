from django.db import models


class Model(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return (self.id and f'{self.__class__.__name__}({self.id})') or f'New {self.__class__.__name__}'


class TimestampedModel(Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
