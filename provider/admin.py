from django.contrib import admin

from provider.models import Vector

# Register your models here.


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "download_number",
        "type",
        "geometry_type",
        "url_server",
        "id_server",
        "path_qgis",
        "state",
        "created_at",
        "updated_at",
    )
