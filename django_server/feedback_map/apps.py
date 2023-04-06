from django.apps import AppConfig


class FvhCourierConfig(AppConfig):
    name = "feedback_map"

    def ready(self):
        """Import signals when app is ready to activate post_save signal."""
        import feedback_map.signals  # noqa
