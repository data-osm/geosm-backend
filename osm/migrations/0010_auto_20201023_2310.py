# Generated by Django 3.1.2 on 2020-10-23 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osm', '0009_auto_20201023_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='querry',
            name='select',
            field=models.TextField(blank=True, default='A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom'),
        ),
    ]
