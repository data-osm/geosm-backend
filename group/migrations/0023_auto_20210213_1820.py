# Generated by Django 3.1.5 on 2021-02-13 18:20

from django.db import migrations, models
import django.db.models.deletion
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0022_auto_20210213_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='layer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='group.layer'),
        )
    ]