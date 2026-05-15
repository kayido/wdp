from django.apps import AppConfig


class AnalyseConfig(AppConfig):
    name = 'analyse'

    def ready(self):
        from . import scheduler
        scheduler.start()
