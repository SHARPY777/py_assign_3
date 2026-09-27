from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Connect the post_save signal that auto-creates the Company
        # profile (and its api_key) whenever a new User is created.
        from . import signals  # noqa: F401
