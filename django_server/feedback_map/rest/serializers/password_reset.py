from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from rest_auth.serializers import PasswordResetSerializer as BasePasswordResetSerializer


class PasswordResetForm(BasePasswordResetForm):
    def save(self, **kwargs):
        kwargs = dict(kwargs, domain_override='app.feedback.fvh.io', use_https=True,
                      from_email=settings.EMAIL_HOST_USER or 'feedback_map@fvh.io')
        return super().save(**kwargs)


class PasswordResetSerializer(BasePasswordResetSerializer):
    password_reset_form_class = PasswordResetForm