# Generated by Django 3.1.7 on 2021-03-12 22:18

from django.db import migrations, models
import genericIcon.models


class Migration(migrations.Migration):

    dependencies = [
        ('genericIcon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='picto',
            name='raster_icon',
            field=models.ImageField(blank=True, null=True, upload_to=genericIcon.models.get_upload_path_layer_icon),
        ),
        migrations.AlterField(
            model_name='picto',
            name='cercle_icon',
            field=models.ImageField(blank=True, null=True, upload_to=genericIcon.models.get_upload_path_layer_icon),
        ),
        migrations.AlterField(
            model_name='picto',
            name='square_icon',
            field=models.ImageField(blank=True, null=True, upload_to=genericIcon.models.get_upload_path_layer_icon),
        ),
    ]
