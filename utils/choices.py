from django.db import models


class ProviderState(models.TextChoices):
    good = "good"
    not_working = "not_working"
    action_require = "action_require"
    unknow = "unknow"


class geometryType(models.TextChoices):
    Polygon = "Polygon"
    Point = "Point"
    LineString = "LineString"
    null = "null"


class ProviderType(models.TextChoices):
    wmts = "wmts"
    wms = "wms"
    wfs = "wfs"


class VectorSourceType(models.TextChoices):
    osm = "osm"
    querry = "querry"
    sigfile = "sigfile"


class groupType(models.TextChoices):
    """differents group types that exists"""

    thematiques = "thematiques"
    base_maps = "base_maps"


class protocolBaseMapChoice(models.TextChoices):
    wmts = "wmts"
    wms = "wms"
