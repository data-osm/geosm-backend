# Generated by Django 3.2.12 on 2022-04-16 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0034_map_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
