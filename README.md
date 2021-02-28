## Create the virtual env and install requirements
```sh
$ python3 -m venv --system-site-packages dataosmenv
$ source dataosmenv/bin/activate 
$ python -m pip install --upgrade pip
$ pip install -r requirements.txt
```
## Migrate the databse 
First create the database
```sh
$ psql postgres
$ create database ...
```

## run the server in prod
```sh
$ docker-compose -f docker-compose-prod.yaml build
$ docker-compose -f docker-compose-prod.yaml up - d
```

## Load icons in prod 
Load icons

```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py loaddata --settings=settings.prod  seed/icon.json
```

### Load OSM data
## If the OSM data  are in a foreign databsae

Edit `import_foreign_osm_table.sql` with the connection parameters of the foreign database and execute it :

```sh
$  psql -d 'your local database -f import_foreign_osm_table.sql 
```
docker-compose -f docker-compose-prod.yaml exec web python manage.py createsuperuser --settings=settings.prod
