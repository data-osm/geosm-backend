# Generated by Django 3.2.12 on 2022-04-08 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0018_vector_download_number'),
        ('osm', '0001_auto_20211106_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleQuerry',
            fields=[
                ('connection', models.TextField(default='default')),
                ('sql', models.TextField(blank=True)),
                ('provider_vector_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='provider.vector')),
                ('auto_update', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='querry',
            name='connection',
            field=models.TextField(default='default'),
        ),
    ]
