# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.operations import HStoreExtension, UnaccentExtension

from django.db import migrations

def create_postgis_extension(apps, schema_editor):
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")


def drop_postgis_extension(apps, schema_editor):
    schema_editor.execute("DROP EXTENSION IF EXISTS postgis;")

def create_postgres_fdw_extension(apps, schema_editor):
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS postgres_fdw;")


def drop_postgres_fdw_extension(apps, schema_editor):
    schema_editor.execute("DROP EXTENSION IF EXISTS postgres_fdw;")


def create_dblink_extension(apps, schema_editor):
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS dblink;")


def drop_dblink_extension(apps, schema_editor):
    schema_editor.execute("DROP EXTENSION IF EXISTS dblink;")

class Migration(migrations.Migration):

    dependencies = [
        ('osm','0012_auto_20201106_2224'),
    ]

    operations = [
        migrations.RunPython(create_postgis_extension, reverse_code=drop_postgis_extension, atomic=True),
        migrations.RunPython(create_postgres_fdw_extension, reverse_code=drop_postgres_fdw_extension, atomic=True),
        migrations.RunPython(create_dblink_extension, reverse_code=drop_dblink_extension, atomic=True),
        HStoreExtension(),
        UnaccentExtension()
    ]