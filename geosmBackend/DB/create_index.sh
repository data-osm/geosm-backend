#!/bin/bash
db='country'
colones=("railway" "shop" "tourism" "power" "amenity" "admin_level" "natural" "name" "sport" "healthcare" "leisure" "highway" "religion" "bridge" "barrier" "historic" "junction" "boundary" "man_made" "place" "office" "aeroway" "landuse" "military" "building" "waterway" )
echo "====== CReation des index ======"
for col in "${colones[@]}";
do
    echo "Creation des index sur la colomne $col"
    psql -d $db  -c 'CREATE INDEX planet_osm_point'${col}'_idx on planet_osm_point("'$col'")'
    psql -d $db  -c 'CREATE INDEX planet_osm_polygon'${col}'_idx on planet_osm_polygon("'$col'")'
    psql -d $db  -c 'CREATE INDEX planet_osm_line'${col}'_idx on planet_osm_line("'$col'")'
done
echo "====== creation des index sur les colomnes terminées ======"
