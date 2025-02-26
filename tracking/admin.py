from django.contrib import admin

from tracking.models import NPSFeedback


@admin.register(NPSFeedback)
class NPSFeedbackAdmin(admin.ModelAdmin):
    list_display = ("score", "has_send_no_response", "date")
    fields = ("score", "has_send_no_response", "date")
    readonly_fields = ("date",)
    list_filter = ("has_send_no_response",)
