# Generated by Django 3.1.5 on 2021-02-13 13:39

from django.db import migrations, models
import django.db.models.deletion
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0021_auto_20210130_2213'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RenameField(
            model_name='layer',
            old_name='metadata',
            new_name='metadata_cap',
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.layer')),
                ('tags', models.ManyToManyField(blank=True, to='group.Tags')),
            ],
        ),
    ]