# apps/assets/apps.py
"""Assets app configuration — registers signals on ready()."""

from django.apps import AppConfig


class AssetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.assets'
    verbose_name       = 'Assets & Transfers'

    def ready(self):
        import apps.assets.signals  # noqa: F401 — connect signal receivers
