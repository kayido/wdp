from django.apps import AppConfig


class AnalyseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyse'

    def ready(self):
        import analyse.signals

# analyse/apps.py
from django.apps import AppConfig

class AnalyseConfig(AppConfig):
    name = 'analyse'

    def ready(self):
        from . import scheduler
        scheduler.start()
