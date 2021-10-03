# Generated by Django 3.2.6 on 2021-08-26 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0011_auto_20210306_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='custom_style',
            old_name='class_name',
            new_name='fucntion_name',
        ),
        migrations.AddField(
            model_name='style',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='group.icon'),
        ),
        migrations.AddField(
            model_name='style',
            name='parameters',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
