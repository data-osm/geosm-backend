create or replace function extend_line(linegeometry geometry, distance_extend int)
   returns geometry 
   language plpgsql
  as
$$
declare newlinegeometry geometry;
BEGIN
SELECT ST_MakeLine(ST_TRANSLATE(a, sin(az1) * len, cos(az1) * 
len),ST_TRANSLATE(b,sin(az2) * len, cos(az2) * len)) as newlinegeometry

  FROM (
    SELECT a, b, ST_Azimuth(a,b) AS az1, ST_Azimuth(b, a) AS az2, ST_Distance(a,b) + distance_extend AS len
      FROM (
        SELECT ST_StartPoint(linegeometry) AS a, ST_EndPoint(linegeometry) AS b
         
    ) AS sub
) AS sub2

INTO 
newlinegeometry;

RETURN newlinegeometry;
END;
$$
;



create or replace function compute_side_and_angle_between_poi_and_roads(poi_geometry point)
   returns json 
   language plpgsql
  as
$$
declare max_distance_from_road integer;
declare road_osm_id integer;
declare distance double precision;
declare angle double precision;
declare direction integer;
declare side integer;


BEGIN
    max_distance_from_road :=300;

    WITH objects AS
        (
			SELECT
            	osm_id,
            	(ST_Dump(planet_osm_roads.way)).geom AS road_geometries
       	 	FROM planet_osm_roads
		)
    SELECT DISTINCT ON
        (ST_Distance(st_setsrid(poi_geometry::geometry,3857), st_setsrid(road_geometries,3857)))
        objects.osm_id as osm_id , 
        ST_Distance(st_setsrid(poi_geometry::geometry,3857), st_setsrid(road_geometries,3857)) as distance 
    FROM objects
        ORDER BY ST_Distance(st_setsrid(poi_geometry::geometry,3857), st_setsrid(road_geometries,3857))
        LIMIT 1
    INTO 
    road_osm_id,
    distance
    ;

    IF road_osm_id is NULL THEN 
     return NULL;
    END IF;

    IF distance > max_distance_from_road THEN  
    return NULL;
    END IF;

	WITH
		road as (SELECT way,st_length(st_transform(way,4326)::geography) as road_length, LEAST(GREATEST(st_LineLocatePoint(way,st_setsrid(poi_geometry::geometry, 3857)), 0.0), 1.0) as poi_on_way_fraction  FROM planet_osm_roads where osm_id=road_osm_id LIMIT 1)
	SELECT
		--direction (-1 left 1 right)
		ST_LineCrossingDirection(way,extend_line(ST_ShortestLine(way,st_setsrid(poi_geometry::geometry,3857)),1)) as direction,
    CASE
        WHEN (poi_on_way_fraction -  1/road_length ) >= 1.0::double precision
              THEN ST_Azimuth(
                  ST_ClosestPoint(way,st_setsrid(poi_geometry::geometry, 3857)),
                  ST_LineInterpolatePoint(way, LEAST(GREATEST(poi_on_way_fraction - 1 / road_length, 0.0), 1.0) )
                )
        ELSE 
        ST_Azimuth(
          ST_ClosestPoint(way,st_setsrid(poi_geometry::geometry, 3857)),
          ST_LineInterpolatePoint(way, LEAST(GREATEST(poi_on_way_fraction + 1 / road_length, 0.0), 1.0) )
        )
    END as angle
		

	FROM

		road

	INTO

		direction,

		angle

	;

  -- IF angle <= pi()/2 THEN
  --   angle = pi()/2 - angle;
  -- END IF;

  -- IF angle > pi()/2 THEN
  --   angle = 2*pi() - angle - - pi()/2;
  -- END IF;


	IF direction=0 THEN --on the road
		side = 0;
	END IF;

	IF direction=-1 OR direction=-2 OR direction=-3  THEN --LEFT
		side = -1;

	END IF;

	IF direction=1 OR direction=2 OR direction=3 THEN --RIGHT
		side = 1;
	END IF;

	RETURN json_build_object('side',side, 'angle', angle, 'osm_id', road_osm_id ) ;

END;
$$
;


ALTER TABLE osm_tables.fonddeplans ADD COLUMN IF NOT EXISTS side INTEGER;
ALTER TABLE osm_tables.fonddeplans ADD COLUMN IF NOT EXISTS angle double precision;

with subquery as (
select osm_id, compute_side_and_angle_between_poi_and_roads(st_setsrid(st_transform(geom, 3857),3857)::Point) as side_and_angle
from osm_tables.fonddeplans
)
update osm_tables.fonddeplans set side=(subquery.side_and_angle->>'side')::integer, angle=(subquery.side_and_angle->>'angle')::double precision
from subquery where osm_tables.fonddeplans.osm_id=subquery.osm_id
-- 3h15 mins