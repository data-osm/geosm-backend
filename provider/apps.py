from django.apps import AppConfig

class ProviderConfig(AppConfig):
    name = 'provider'
    def ready(self):
        import provider.signals