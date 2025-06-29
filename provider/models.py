import os
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.functions import Coalesce, JSONObject, TruncDate
from django.forms import ValidationError
from tracking_fields.decorators import track
from tracking_fields.models import UPDATE, TrackedFieldModification, TrackingEvent

from group.subModels.icon import Icon
from utils.choices import ProviderState, ProviderType, VectorSourceType, geometryType

from .qgis.manageStyle import (
    add_style_qml_from_string_to_layer,
    get_thumbnail_from_style_of_layer,
    remove_style,
    update_style,
)


class VectorQuerySet(models.QuerySet):
    def with_download_logs_count(self):
        return self.annotate(
            download_logs_count=Coalesce(
                models.Subquery(
                    TrackedFieldModification.objects.filter(
                        field="download_number",
                        event__in=TrackingEvent.objects.filter(
                            object_id=models.OuterRef(
                                models.OuterRef("provider_vector_id")
                            ),
                            object_content_type=ContentType.objects.get_for_model(
                                self.model
                            ),
                            action=UPDATE,
                        ).values_list("pk", flat=True),
                    )
                    .values("field")
                    .annotate(cnt=models.Count("*"))
                    .values("cnt")[:1]
                ),
                0,
            )
        )


@track(
    "name", "url_server", "id_server", "path_qgis", "table", "count", "download_number"
)
class Vector(models.Model):
    """model of a vector provider. it represent a data and is store in a schema and table"""

    objects = VectorQuerySet.as_manager()

    provider_vector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True, default=None, unique=True)
    type = models.TextField(
        max_length=15, null=True, blank=True, choices=VectorSourceType.choices
    )
    table = models.TextField(max_length=15, null=True, default=None)
    """ the table where data are store """
    shema = models.TextField(max_length=15, null=True, default=None)
    """ the shema where data are store """
    geometry_type = models.CharField(max_length=11, choices=geometryType.choices)
    """ the geometry_type of the querry """
    url_server = models.URLField(null=True)
    """ url of the carto server """
    id_server = models.CharField(max_length=50, null=True, default=None)
    """ identifiant of this ressource in the carto server """
    path_qgis = models.CharField(max_length=250, null=True, blank=True, default=None)
    """ Path to QGIS project """
    extent = ArrayField(
        models.FloatField(), size=4, null=True, blank=True, default=None
    )
    """ extent of this ressource """
    z_min = models.IntegerField(null=False, default=0)
    z_max = models.IntegerField(null=False, default=24)
    count = models.IntegerField(null=True)
    """ number of feature of this ressources """
    total_lenght = models.IntegerField(null=True)
    """ total lenght of the ressource if geometry type is LineString """
    total_area = models.IntegerField(null=True)
    """ total area of the ressource if geometry type is Polygon """
    epsg = models.IntegerField(null=True, default=None)
    state = models.CharField(max_length=20, choices=ProviderState.choices, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_number = models.IntegerField(default=0)
    primary_key_field = models.CharField(max_length=50, null=False, default="osm_id")
    """ primary key field of the table """

    class Meta:
        unique_together = (
            "id_server",
            "path_qgis",
        )

    @transaction.atomic
    def increment_download_number(self):
        self.download_number += 1
        self.save()

    def get_download_logs(self):
        return (
            TrackedFieldModification.objects.filter(
                field="download_number",
                event__in=TrackingEvent.objects.filter(
                    object_id=self.provider_vector_id,
                    object_content_type=ContentType.objects.get_for_model(self),
                    action=UPDATE,
                ).values_list("pk", flat=True),
            )
            .annotate(updated_on=TruncDate("event__date"))
            .values("updated_on")
            .annotate(total_amount=models.Count("pk"))
            .values(cnt=models.Count("*"))
            .values_list(
                JSONObject(
                    total_amount=models.F("total_amount"), date=models.F("updated_on")
                ),
                flat=True,
            )
        )


class External(models.Model):
    """model of a external provider : data are not stre in the app DB"""

    provider_external_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    protocol_carto = models.CharField(max_length=5, choices=ProviderType.choices)
    url_server = models.URLField(null=True)
    """ url of the carto server """
    id_server = models.CharField(max_length=50)
    """ identifiant of this ressource in the carto server """
    extent = models.TextField(null=True)
    """ extent of this ressource """
    z_min = models.IntegerField(null=True)
    z_max = models.IntegerField(null=True)
    epsg = models.IntegerField()


def get_custom_style_icon_path(instance, filename):
    return os.path.join("pictoQgis", filename)


def get_custom_qml_path(instance, filename):
    directory = re.sub("[^A-Za-z0-9]+", "", "qml")
    return os.path.join(directory, instance.name + "_" + str(instance.pk) + ".qml")


class Custom_style(models.Model):
    """model that store custom and parametrable QGIS styles"""

    custom_style_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=400, blank=True)
    icon = models.ImageField(
        blank=True, null=False, default=None, upload_to="customStyle/"
    )
    function_name = models.CharField(max_length=50, blank=True)
    """ name of the class responsible to format QML """
    geometry_type = models.CharField(max_length=11, choices=geometryType.choices)


@track("name", "qml_file", "qml")
class Style(models.Model):
    """model that store name, qml, ol style of a provider (raster and vector)"""

    provider_style_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    qml = models.TextField()
    ol = models.TextField(blank=True)
    pictogram = models.ImageField(blank=True)
    provider_vector_id = models.ForeignKey(Vector, on_delete=models.CASCADE)
    custom_style_id = models.ForeignKey(
        Custom_style, on_delete=models.SET_NULL, blank=True, null=True
    )
    icon = models.ForeignKey(Icon, on_delete=models.RESTRICT, null=True, blank=True)
    qml_file = models.FileField(
        blank=True, null=True, default=None, upload_to=get_custom_qml_path
    )
    parameters = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    """ just use in order to write the content of the file in the field qml. ie: the file never exist"""

    class Meta:
        unique_together = (
            "name",
            "provider_vector_id",
        )

    def save(self, *args, **kwargs):
        """save or update a style"""

        self.name = re.sub("[^A-Za-z0-9]+", "", self.name)

        if self.pk:
            previous_style = Style.objects.get(pk=self.pk)
            self.name = previous_style.name
            if previous_style.qml_file != self.qml_file:
                qml_content = None
                self.qml_file.open(mode="r")
                qml_content = self.qml_file.read()
                self.qml = qml_content

                response_update_style = update_style(
                    self.provider_vector_id.id_server,
                    self.provider_vector_id.path_qgis,
                    previous_style.name,
                    self.name,
                    qml_content,
                )

                if response_update_style.error:
                    raise ValidationError(
                        response_update_style.msg
                        + " : "
                        + str(response_update_style.description)
                    )

                Path(os.path.join(settings.MEDIA_ROOT, "pictoQgis")).mkdir(
                    parents=True, exist_ok=True
                )
                if os.path.exists(self.pictogram.name):
                    path = self.pictogram.name
                else:
                    path = os.path.join(
                        settings.MEDIA_ROOT, "pictoQgis", str(uuid.uuid4()) + ".png"
                    )

                get_thumbnail_from_style_of_layer(
                    self.provider_vector_id.id_server,
                    self.provider_vector_id.path_qgis,
                    self.name,
                    path,
                )
                self.pictogram.name = path

        else:
            self.qml_file.open(mode="rb")
            qml_content = self.qml_file.read()
            if isinstance(qml_content, str) is False:
                qml_content = qml_content.decode("utf-8")
            self.qml = qml_content

            tmp_file = os.path.join(settings.TEMP_URL, str(uuid.uuid1()) + ".qml")
            default_storage.save(tmp_file, ContentFile(qml_content))

            response_add_style = add_style_qml_from_string_to_layer(
                self.provider_vector_id.id_server,
                self.provider_vector_id.path_qgis,
                self.name,
                qml_content,
                tmp_file,
            )
            if response_add_style.error:
                raise ValidationError(
                    response_add_style.msg + " : " + str(response_add_style.description)
                )
            Path(os.path.join(settings.MEDIA_ROOT, "pictoQgis")).mkdir(
                parents=True, exist_ok=True
            )
            picto_path = os.path.join("pictoQgis", str(uuid.uuid4()) + ".png")
            path = os.path.join(settings.MEDIA_ROOT, picto_path)

            get_thumbnail_from_style_of_layer(
                self.provider_vector_id.id_server,
                self.provider_vector_id.path_qgis,
                self.name,
                path,
            )
            self.pictogram.name = picto_path

        super(Style, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete a style"""
        response_remove_style = remove_style(
            self.provider_vector_id.id_server,
            self.provider_vector_id.path_qgis,
            self.name,
        )
        if response_remove_style.error:
            raise ValidationError(
                response_remove_style.msg
                + " : "
                + str(response_remove_style.description)
            )
        super(Style, self).delete(*args, **kwargs)
