# Generated by Django 3.1.1 on 2020-09-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='osm_querry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('osm_querry_id', models.IntegerField()),
                ('select_clause', models.TextField()),
                ('where_clause', models.TextField()),
                ('geometry_type', models.CharField(choices=[('Polygon', 'Polygon'), ('Point', 'Point'), ('LineString', 'Linestring')], max_length=11)),
            ],
        ),
    ]
