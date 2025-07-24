from django.contrib import admin

from tracking.models import NPSFeedback, OsmUpdateLog


@admin.register(NPSFeedback)
class NPSFeedbackAdmin(admin.ModelAdmin):
    list_display = ("score", "has_send_no_response", "date")
    fields = ("score", "has_send_no_response", "date")
    readonly_fields = ("date",)
    list_filter = ("has_send_no_response",)


@admin.register(OsmUpdateLog)
class OsmUpdateLogAdmin(admin.ModelAdmin):
    list_display = ("osm_id", "osm_type", "created")
    fields = ("osm_id", "osm_type", "created")
    readonly_fields = ("created",)
