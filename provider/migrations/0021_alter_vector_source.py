# Generated by Django 3.2.13 on 2022-06-25 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0020_vector_primary_key_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vector',
            name='source',
            field=models.TextField(blank=True, choices=[('osm', 'Osm'), ('querry', 'Querry'), ('sigfile', 'Sigfile')], max_length=15, null=True),
        ),
    ]
