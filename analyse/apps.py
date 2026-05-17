from django.apps import AppConfig


class AnalyseConfig(AppConfig):
    name = 'analyse'

    def ready(self):
        import analyse.signals
        from . import scheduler
        scheduler.start()
