## run the server in prod
```sh
$ docker-compose -f docker-compose-prod.yaml build
$ docker-compose -f docker-compose-prod.yaml up - d
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  seedCustomStyle --settings=settings.prod
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py createsuperuser --settings=settings.prod
```

## Load OSM data
### Import OSM data in foreign database [import_osm.MD](geosmBackend/DB/import_osm.MD)
### Link the foreign and the local database

Edit [import_foreign_osm_table.sql](import_foreign_osm_table.sql) with the connection parameters of the foreign database and execute it :

```sh
$  docker-compose exec --user postgres db psql -d postgres -f /import_foreign_osm_table.sql 
```

## Setup elasticsearch
```sh
docker-compose  exec web python manage.py search_index --rebuild --settings=settings.dev
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  search_index --rebuild --settings=settings.prod  
```

## Load icons in prod 
Load icons
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py loaddata --settings=settings.prod  seed/icon.json
```