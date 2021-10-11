# Generated by Django 3.1.5 on 2021-02-13 18:20

from django.db import migrations, models
import django.db.models.deletion
import group.models

class Migration(migrations.Migration):

    dependencies = [
        ('group', '0023_auto_20210213_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='icon_path',
            field=models.FileField(default='', upload_to=group.models.get_upload_path_group_icon),
            preserve_default=False,
        ) 
    ]