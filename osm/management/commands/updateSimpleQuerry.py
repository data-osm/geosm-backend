from django.core.management import color
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, Error
from django.http.request import QueryDict
from psycopg2.extensions import AsIs
import traceback
from django.conf import settings
from provider.models import Vector
from osm.models import SimpleQuerry
from django.core.files import File
import pathlib
from os.path import join, exists, basename
from os import makedirs, name, path
from shutil import copyfile
from csv import reader
from django.db import transaction
import json
from typing import Callable, Any, List

class Command(BaseCommand):
    help = 'Update simple querrys providers'

    def handle(self, *args, **options):
        count = SimpleQuerry.objects.count()
        i=1
        for querry in SimpleQuerry.objects.all():
            simpleQuerry:SimpleQuerry=querry
            simpleQuerry.save()
            self.stdout.write(self.style.SUCCESS(str(i)+'/'+str(count)))
            i=1+i
        self.stdout.write(self.style.SUCCESS('All the simple querries have been successfuly updated'))  