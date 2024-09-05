#!/bin/bash

SETTINGS_ENV="settings.${ENV:=dev}" 

pip install --upgrade pip
pip install -r requirements-lock.txt

python manage.py migrate  --settings=$SETTINGS_ENV
python manage.py runserver --settings=$SETTINGS_ENV  0.0.0.0:8000


