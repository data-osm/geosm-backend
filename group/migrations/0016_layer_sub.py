# Generated by Django 3.1.4 on 2020-12-05 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0015_delete_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='sub',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='group.sub'),
            preserve_default=False,
        ),
    ]