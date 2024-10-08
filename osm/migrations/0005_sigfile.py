# Generated by Django 3.2.13 on 2022-06-18 20:03

from django.db import migrations, models
import django.db.models.deletion
import osm.subModels.sigFile


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0019_vector_source'),
        ('osm', '0004_alter_simplequerry_auto_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='sigFile',
            fields=[
                ('connection', models.TextField(default='default')),
                ('file', models.FileField(blank=True, default=None, null=True, upload_to=osm.subModels.sigFile.get_custom_file_path)),
                ('provider_vector_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='provider.vector')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
