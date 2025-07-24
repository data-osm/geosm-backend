from django.db import models


class NPSFeedback(models.Model):
    score = models.IntegerField(null=True, blank=True)
    has_send_no_response = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class OsmUpdateLog(models.Model):
    osm_id = models.IntegerField()
    osm_type = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
