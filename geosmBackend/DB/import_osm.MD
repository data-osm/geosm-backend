Make sure you already have osm2pgsql, wget install on your machine,### Download the OSM PBF of your region on [GEOFABRIK](https://download.geofabrik.de/)
```sh
    mkdir geosmBackend/DB/working_dir
    cd geosmBackend/DB/working_dir
    wget https://download.geofabrik.de/africa/cameroon-latest.osm.pbf -O osm.pbf 
```
### Import OSM PBF in database
Create a database with name $db (choose your favorite name)
Replace $db by the name of your database
```sh
$ osm2pgsql --cache 10000 --number-processes 5 --extra-attributes --slim -G -c -U postgres -d $db -H localhost -W --hstore-all -S ./data-osm.style osm.pbf
$ chmod +x ../create_index.sh
$ ../create_index.sh
```
To update the map: 
- get the state at a particcar date and time : wget "https://replicate-sequences.osm.mazdermind.de/?"`date -u +"%Y-%m-%d"`"T00:00:00Z" -O $WORKOSM_DIR/state.txt
- baseUrl in cnfiguration file : https://planet.openstreetmap.org/replication/minute/
