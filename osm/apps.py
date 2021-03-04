from django.apps import AppConfig


class OsmConfig(AppConfig):
    name = 'osm'
    def ready(self):
        import osm.signals
