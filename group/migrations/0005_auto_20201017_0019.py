# Generated by Django 3.1.2 on 2020-10-17 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_auto_20201017_0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icon',
            name='icon_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
