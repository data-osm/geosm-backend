from django.core.management.base import BaseCommand
from osm.models import Querry


class Command(BaseCommand):
    help = "Update OSM provider"

    def handle(self, *args, **options):
        count = Querry.objects.filter(auto_update=True).count()
        i = 1
        for query in Querry.objects.filter(auto_update=True)[2:]:
            osm_query: Querry = query
            osm_query.save()
            self.stdout.write(self.style.SUCCESS(str(i) + "/" + str(count)))
            i = 1 + i
        self.stdout.write(
            self.style.SUCCESS("All the OSM queries, have been successfully updated")
        )
