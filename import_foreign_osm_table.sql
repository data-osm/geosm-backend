CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SERVER osm_server
   FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'host', port 'port', dbname 'dbname');
  
CREATE USER MAPPING FOR USER
   SERVER osm_server
  OPTIONS (user 'user', password 'userpass');

IMPORT FOREIGN SCHEMA public LIMIT TO (planet_osm_point, planet_osm_polygon, planet_osm_line)
  FROM SERVER osm_server
  INTO public;
  
