from django.apps import AppConfig


class ComplaintConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.complaint'
    def save(self):
        from . import signals