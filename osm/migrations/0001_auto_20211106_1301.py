# Generated by Django 3.2.8 on 2021-11-06 13:01

from django.db import migrations, models
import django.utils.timezone
from datetime import datetime

class Migration(migrations.Migration):

    dependencies = [
        ('osm', 'setup_extensions'),
    ]

    operations = [
        migrations.AddField(
            model_name='querry',
            name='auto_update',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='querry',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='querry',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]