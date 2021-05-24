## run the server in prod
```sh
$ create database ...
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
docker-compose  exec web python manage.py makemigrations --settings=settings.dev

docker-compose  exec web python manage.py search_index --rebuild --settings=settings.dev

<!-- INSERT INTO public.planet_osm_polygon(osm_id, admin_level , name , way)
	SELECT id, 'roi' , nom, st_transform(ST_SetSRID(geom, 4326),3857) FROM public.instances_gc;  -->