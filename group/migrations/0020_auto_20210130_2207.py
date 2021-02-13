# Generated by Django 3.1.5 on 2021-01-30 22:07

from django.db import migrations, models
import django.db.models.deletion
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0010_auto_20201122_1154'),
        ('group', '0019_group_icon_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer_provider_style',
            name='layer_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.layer'),
        ),
        migrations.AlterField(
            model_name='layer_provider_style',
            name='vp_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='provider.vector'),
        ),
        migrations.AlterField(
            model_name='layer_provider_style',
            name='vs_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='provider.style'),
        )
    ]
