## Duplicate DATA OSM

1) create an environment file .env in settings folder as .env.sample

For dev purpose use `docker-compose-dev.yaml`, for prod use `docker-compose-prod.yaml`

2) build and pull docker images 
```sh
$ docker-compose -f docker-compose-prod.yaml build
```
3) lunch the backend 
```sh
$ docker-compose -f docker-compose-prod.yaml up -d
```
4) Enable custom Style configurations
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  seedCustomStyle --settings=settings.prod
```
5) create a super user, you will use this credentials after
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  createsuperuser --settings=settings.prod
```
6) Setup elasticsearch
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  search_index --rebuild --settings=settings.prod  
```
7) Load icons in prod 
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py loaddata --settings=settings.prod  seed/icon.json
```
At this step your project is ready. To import OSM DATA, jump to Load OSM DATA section describe below


## Load OSM data

### Import OSM data in  database [import_osm.MD](geosmBackend/DB/import_osm.MD)

### Link a foreign database containing osm data with our database

Edit [import_foreign_osm_table.sql](import_foreign_osm_table.sql) with the connection parameters of the foreign database and execute it :

```sh
$  docker-compose -f docker-compose-prod.yaml exec --user postgres db psql -d postgres -f /import_foreign_osm_table.sql 
```


### For kibana use
https://stackoverflow.com/questions/42385977/accessing-a-docker-container-from-another-container

docker run --network host --name kibana -e "ELASTICSEARCH_HOSTS=http://127.0.0.1:9200" -p 5601:5601 kibana:7.17.0

## Backup database and files: 

### Dabase
pg_dump --clean --exclude-schema osm_tables --exclude-schema sigfile --exclude-table 'planet_osm*' --no-acl --no-owner -d <database_name> -U <database_user>  -h <database_host> -W  | gzip >  /path/to_store/data_osm_dump_$(date '+%Y-%m-%d_%H_%M_%S').sql.gz

### Files to backup
icons/group/
icons/layer/
icons/picto/
icons/pictoQgis/
icons/Autres/
icons/sig-file/

## Maintenance 

To regenerate a layer 
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  reGenerateQgisProject <vector_id_of_the_layer>  --settings=settings.prod  
```
To regenerate all layers (can take much time)
```sh
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  reGenerateQgisProject --settings=settings.prod  
```