# Generated by Django 3.1.1 on 2020-09-20 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='External',
            fields=[
                ('provider_external_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('protocol_carto', models.CharField(choices=[('wmts', 'Wmts'), ('wms', 'Wms'), ('wfs', 'Wfs')], max_length=5)),
                ('url_server', models.URLField(null=True)),
                ('id_server', models.CharField(max_length=50)),
                ('extent', models.TextField(null=True)),
                ('z_min', models.IntegerField(null=True)),
                ('z_max', models.IntegerField(null=True)),
                ('epsg', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Vector',
            fields=[
                ('provider_vector_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('table', models.TextField()),
                ('shema', models.TextField()),
                ('geometry_type', models.CharField(choices=[('Polygon', 'Polygon'), ('Point', 'Point'), ('LineString', 'Linestring')], max_length=11)),
                ('url_server', models.URLField(null=True)),
                ('id_server', models.CharField(max_length=50)),
                ('extent', models.TextField(null=True)),
                ('z_min', models.IntegerField(null=True)),
                ('z_max', models.IntegerField(null=True)),
                ('count', models.IntegerField(null=True)),
                ('total_lenght', models.IntegerField(null=True)),
                ('total_area', models.IntegerField(null=True)),
                ('epsg', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('provider_style_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('qml', models.TextField()),
                ('ol', models.TextField()),
                ('pictogram', models.ImageField(upload_to='')),
                ('vector_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='provider.vector')),
            ],
        ),
    ]
