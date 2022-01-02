## run the server in prod
```sh
$ docker-compose -f docker-compose-prod.yaml build
$ docker-compose -f docker-compose-prod.yaml up - d
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py  seedCustomStyle --settings=settings.prod
$ docker-compose -f docker-compose-prod.yaml exec web python manage.py createsuperuser --settings=settings.prod
```

## Load OSM data
### If the OSM data  are in a foreign databsae

Edit `import_foreign_osm_table.sql` with the connection parameters of the foreign database and execute it :

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

### For kibana use
https://stackoverflow.com/questions/42385977/accessing-a-docker-container-from-another-container

docker run --network host --name kibana -e "ELASTICSEARCH_HOSTS=http://172.17.0.1:9200" -p 5601:5601 kibana:7.10.1 