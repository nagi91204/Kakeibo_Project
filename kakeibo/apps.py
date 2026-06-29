from django.apps import AppConfig


class KakeiboConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kakeibo'

    def ready(self):
        from . import signals  # noqa: F401
