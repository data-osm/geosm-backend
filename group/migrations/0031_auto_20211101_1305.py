# Generated by Django 3.2.8 on 2021-11-01 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0030_auto_20210312_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='icon',
            name='category',
            field=models.TextField(default='Autres'),
        ),
    ]
