# Generated by Django 3.1.5 on 2021-01-10 12:16

from django.db import migrations, models
import django.db.models.deletion
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0010_auto_20201122_1154'),
        ('group', '0016_layer_sub'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer_provider_style',
            fields=[
                ('layer_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, serialize=False, to='group.layer')),
                ('vp_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='provider.vector')),
                ('vs_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='provider.style')),
            ],
        ),
    ]
