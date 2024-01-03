import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import color
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, Error
from django.http.request import QueryDict
from psycopg2.extensions import AsIs
import traceback
from django.conf import settings
from provider.models import Vector, Style
from osm.models import Querry
from django.core.files import File
import pathlib
from os.path import join, exists, basename
from os import makedirs, name, path, remove
from shutil import copyfile
from csv import reader
from django.db import transaction
import json
from typing import Callable, Any, List
from django.conf import settings

from provider.qgis.manageVectorLayer import addVectorLayerFomPostgis
from provider.qgis.manageStyle import updateStyle, addStyleQMLFromStringToLayer


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

        if "vector_id" in options:
            providers: List[Vector] = Vector.objects.filter(
                url_server=Vector.objects.get(pk=options["vector_id"]).url_server
            )
        else:
            providers: List[Vector] = Vector.objects.filter(url_server__isnull=False)
        """
            - supprimer le projet qgis 
            - ajouter les couches au projet (il va etre automatiquement cree)
            - Appliquer chaque style
        """
        for provider in providers:
            qgisProject = provider.url_server.replace(
                OSMDATA["url_qgis_server_prefix"], ""
            )
            if exists(join(project_qgis_path, qgisProject)):
                remove(join(project_qgis_path, qgisProject))
        i = 0
        for provider in providers:
            qgisProject = provider.url_server.replace(
                OSMDATA["url_qgis_server_prefix"], ""
            )
            createOSMDataSourceResponse = addVectorLayerFomPostgis(
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
                qgisProject,
            )

            if createOSMDataSourceResponse.error == False:
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
                        updateStyleRes = updateStyle(
                            provider.id_server,
                            qgisProject,
                            style.name,
                            style.name,
                            style.qml,
                        )
                        if updateStyleRes.error == False:
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
                            self.stdout.write(
                                self.style.ERROR(
                                    "Could not updated style "
                                    + style.name
                                    + "  "
                                    + ". Error description: "
                                    + updateStyleRes.msg
                                    + " => "
                                    + updateStyleRes.description
                                )
                            )
                    else:
                        tmp_file = join(settings.TEMP_URL, str(uuid.uuid1()) + ".qml")
                        default_storage.save(tmp_file, ContentFile(style.qml))
                        addStyleRes = addStyleQMLFromStringToLayer(
                            provider.id_server,
                            provider.path_qgis,
                            style.name,
                            style.qml,
                            tmp_file,
                        )
                        if addStyleRes.error == False:
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
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    "Could not add style "
                                    + style.name
                                    + "  "
                                    + ". Error description: "
                                    + addStyleRes.msg
                                    + " => "
                                    + addStyleRes.description
                                )
                            )

            else:
                self.stdout.write(
                    self.style.ERROR(
                        "Could not add provider "
                        + provider.name
                        + " to  "
                        + qgisProject
                        + ". Error description: "
                        + createOSMDataSourceResponse.msg
                        + " => "
                        + createOSMDataSourceResponse.description
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
