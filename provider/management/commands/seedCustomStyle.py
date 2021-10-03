from django.core.management.base import BaseCommand, CommandError
from django.db import connection, Error
from psycopg2.extensions import AsIs
import traceback
from django.conf import settings
from provider.models import Custom_style
from django.core.files import File
import pathlib
from os.path import join, exists
from os import makedirs
from shutil import copyfile

class Command(BaseCommand):
    help = 'Add or update custom styles'

    def handle(self, *args, **options):

        try:
            self._addOrUpdateeCluster()
            self.stdout.write(self.style.SUCCESS('Successfully add all custom Style' ))
        except Exception as e:
            traceback.print_exc()
            self.stdout.write(self.style.ERROR(str(e)))

    def _addOrUpdateeCluster(self):
        customFile, created = Custom_style.objects.get_or_create(
            name='Point cluster',
            geometry_type='Point',
            defaults={
                'description': "Condense multiple overlapping or nearby points into a single rendered marker for clarity. The clusters that are generated shows the number of items in each cluster, and as a user pans the map the clusters adjust based on the view. This makes it more efficient to render highly condensed data and easier for users to understand the map. ",
                'fucntion_name':"pointCluster",
            }
        )
        iconPath = join(pathlib.Path(__file__).parent.resolve(),'images/pointCluster.png')
        customStyleDir = join(settings.MEDIA_ROOT,'customStyle')
        if not exists(customStyleDir):
            makedirs(customStyleDir)
        copyfile(iconPath, join(customStyleDir,'pointCluster.png'))

        # customFile.icon = join('customStyle','pointCluster.png')
        customFile.icon.name = join('customStyle','pointCluster.png')
        customFile.save()

        self.stdout.write(self.style.SUCCESS('Successfully add/update Custom Style Point Cluster' ))
