from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from provider.models import Vector

# Register your models here.


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "download_number",
        "download_logs_count",
        "type",
        "geometry_type",
        "url_server",
        "id_server",
        "path_qgis",
        "state",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Infos générales",
            {
                "fields": (
                    "name",
                    "type",
                    "state",
                    "geometry_type",
                    "download_number",
                    "download_logs_count",
                )
            },
        ),
        (
            "Serveur cartographique",
            {
                "fields": (
                    "url_server",
                    "id_server",
                    "path_qgis",
                )
            },
        ),
        ("Téléchargement", {"fields": ("download_logs",)}),
        ("Logs", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = (
        "type",
        "state",
        "geometry_type",
        "download_logs",
        "download_logs_count",
        "download_number",
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).with_download_logs_count()  # type: ignore

    def download_logs_count(self, obj: Vector) -> int:
        return obj.download_logs_count  # type: ignore

    @admin.display(description="Logs de téléchargement")
    def download_logs(self, obj: Vector):
        base = """
        <table>
            <thead>
                <tr>
                    <th>Total</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
        row_tpl = "<tr><td>{total}</td><td>{date}</td></tr>"
        rows = ""
        for log in list(obj.get_download_logs()):
            rows += row_tpl.format(
                total=log["total_amount"],
                date=log["date"],
            )

        return mark_safe(base.format(rows=rows))
