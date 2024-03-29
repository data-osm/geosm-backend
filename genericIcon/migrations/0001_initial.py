# Generated by Django 3.1.7 on 2021-03-12 21:51

from django.db import migrations, models
import django.db.models.deletion
import genericIcon.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0029_auto_20210307_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background', models.CharField(max_length=30)),
                ('color', models.CharField(blank=True, max_length=30, null=True)),
                ('cercle_icon', models.ImageField(upload_to=genericIcon.models.get_upload_path_layer_icon)),
                ('square_icon', models.ImageField(upload_to=genericIcon.models.get_upload_path_layer_icon)),
                ('icon', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='group.icon')),
            ],
        ),
    ]
