Make sure you already have osm2pgsql, wget install on your machine,### Download the OSM PBF of your region on [GEOFABRIK](https://download.geofabrik.de/)
```sh
    cd geosmBackend/DB/working_dir
    wget https://download.geofabrik.de/africa/cameroon-latest.osm.pbf -O osm.pbf 
```
### Import OSM PBF in database
Replace $db by the name of your database
```sh
osm2pgsql --cache 10000 --number-processes 5 --extra-attributes --slim -G -c -U postgres -d $db -H localhost -W --hstore-all -S ../data-osm.style osm.pbf
chmod +x ../create_index.sh
../create_index.sh
```
nohup osm2pgsql --cache 25000 --number-processes 6 --proj 2154 --extra-attributes --slim -G -c -U postgres -d france -H localhost -W --hstore-all -S ./default.style osm.pbf &