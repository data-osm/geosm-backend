# Generated by Django 3.1.5 on 2021-01-30 21:41

from django.db import migrations, models
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0018_auto_20210115_1245'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='layer_provider_style',
            unique_together=set([('vp_id', 'layer_id')]),
        ),
    ]