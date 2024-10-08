Make sure you already have osm2pgsql, wget install on your machine,
### Download the OSM PBF of your region on [GEOFABRIK](https://download.geofabrik.de/)
```sh
    mkdir geosmBackend/DB/working_dir
    cd geosmBackend/DB/working_dir
    wget https://download.geofabrik.de/africa/cameroon-latest.osm.pbf -O osm.pbf 
```
### Import OSM PBF in database
- Import OSM PBF in database using osm2pgsql 
- Create index on created tables
```sh
$ osm2pgsql --cache 10000 --number-processes 5 --extra-attributes --slim -G -c -U postgres -d <database_name> -H localhost -W --hstore-all -S ../data-osm.style osm.pbf
$ chmod +x ../create_index.sh
$ ../create_index.sh <database_name>
```

### To keep update the OSM data: 
More information here : https://github.com/Magellium/magosm_db

- get the state at a particular date and time : wget "https://replicate-sequences.osm.mazdermind.de/?"`date -u +"%Y-%m-%d"`"T00:00:00Z" -O $WORKOSM_DIR/state.txt
- baseUrl in configuration file : https://planet.openstreetmap.org/replication/minute/
