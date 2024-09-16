import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.conf import settings
from provider.models import Vector, Style
from os.path import join, exists
from os import remove
from typing import List

from provider.qgis.manageVectorLayer import (
    add_vector_layer_from_postgis,
    addVectorLayerFromPostgisException,
)
from provider.qgis.manageStyle import (
    AddStyleException,
    UpdateStyleException,
    add_style_qml_from_string_to_layer,
    update_style,
)


class Command(BaseCommand):
    help = "Update OSM provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "vector_id",
            nargs="?",
            default=None,
            type=str,
            help="Specify the id of the layer you wish to regenarate the QGIS Project",
        )

    def handle(self, *args, **options):
        OSMDATA = settings.OSMDATA
        DATABASES = settings.DATABASES
        project_qgis_path = OSMDATA["project_qgis_path"]

        if options.get("vector_id"):
            providers: List[Vector] = Vector.objects.filter(
                url_server=Vector.objects.get(pk=options["vector_id"]).url_server
            )
        else:
            providers: List[Vector] = Vector.objects.filter(url_server__isnull=False)
        """
            - supprimer le projet qgis 
            - ajouter les couches au projet (il va être automatiquement Cree)
            - Appliquer chaque style
        """
        for provider in providers:
            qgis_project = provider.url_server.replace(
                OSMDATA["url_qgis_server_prefix"], ""
            )
            if exists(join(project_qgis_path, qgis_project)):
                remove(join(project_qgis_path, qgis_project))
        i = 0
        for provider in providers:
            qgis_project = provider.url_server.replace(
                OSMDATA["url_qgis_server_prefix"], ""
            )
            try:
                add_vector_layer_from_postgis(
                    DATABASES["default"]["HOST"],
                    DATABASES["default"]["PORT"],
                    DATABASES["default"]["NAME"],
                    DATABASES["default"]["USER"],
                    DATABASES["default"]["PASSWORD"],
                    provider.shema,
                    provider.table,
                    "geom",
                    "osm_id",
                    provider.table,
                    qgis_project,
                )
            except addVectorLayerFromPostgisException as error:
                self.stdout.write(
                    self.style.ERROR(
                        "Could not add provider "
                        + provider.name
                        + " to  "
                        + qgis_project
                        + ". Error description: "
                        + error.msg
                        + " => "
                        + error.description
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully add layer "
                        + provider.name
                        + "  "
                        + str(i)
                        + "/"
                        + str(len(providers))
                    )
                )
                i = i + 1

                styleIndex = 0
                styles: List[Style] = Style.objects.filter(provider_vector_id=provider)
                for style in styles:
                    if style.name == "default" or style.name == "defaut":
                        try:
                            update_style(
                                provider.id_server,
                                qgis_project,
                                style.name,
                                style.name,
                                style.qml,
                            )
                        except UpdateStyleException as error:
                            self.stdout.write(
                                self.style.ERROR(
                                    "Could not updated style "
                                    + style.name
                                    + "  "
                                    + ". Error description: "
                                    + error.msg
                                    + " => "
                                    + error.description
                                )
                            )
                        else:
                            styleIndex = styleIndex + 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    "Successfully updated style "
                                    + style.name
                                    + "  "
                                    + str(styleIndex)
                                    + "/"
                                    + str(len(styles))
                                )
                            )

                    else:
                        tmp_file = join(settings.TEMP_URL, str(uuid.uuid1()) + ".qml")
                        default_storage.save(tmp_file, ContentFile(style.qml))
                        try:
                            add_style_qml_from_string_to_layer(
                                provider.id_server,
                                provider.path_qgis,
                                style.name,
                                style.qml,
                                tmp_file,
                            )
                        except AddStyleException as error:
                            self.stdout.write(
                                self.style.ERROR(
                                    "Could not add style "
                                    + style.name
                                    + "  "
                                    + ". Error description: "
                                    + error.msg
                                    + " => "
                                    + error.description
                                )
                            )
                        else:
                            styleIndex = styleIndex + 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    "Successfully add style "
                                    + style.name
                                    + "  "
                                    + str(styleIndex)
                                    + "/"
                                    + str(len(styles))
                                )
                            )

        self.stdout.write(
            self.style.SUCCESS(
                str(i)
                + " / "
                + str(len(providers))
                + " providers have been successfuly add to a QGIS Project"
            )
        )
