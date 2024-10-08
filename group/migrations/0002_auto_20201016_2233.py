# Generated by Django 3.1.2 on 2020-10-16 22:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='icon',
            name='category',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='icon',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), size=10),
        ),
    ]
