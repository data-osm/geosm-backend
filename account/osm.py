import logging

import osmapi
import requests
from django.conf import settings
from django.db import DatabaseError, connection, models
from django.http import HttpRequest
from osmapi import errors
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class OSMFeatureType(models.Choices):
    NODE = "node"
    WAY = "way"
    RELATION = "relation"


class GetOsmParentBuildingException(Exception):
    pass


class OsmUserInfoException(Exception):
    pass


class OsmFeatureUpdateException(Exception):
    pass


class OsmLocalFeatureUpdateException(Exception):
    pass


def get_osm_user_info(request: HttpRequest) -> dict:
    access_token = None
    if request.session.get("osm_token", None) is not None:
        access_token = request.session["osm_token"]
    if request.user and getattr(request.user, "osm_token", None) is not None:  # type: ignore
        access_token = request.user.osm_token  # type: ignore

    if access_token is None:
        raise OsmUserInfoException("osm_token non trouvé")

    def parse_osm_user_info(xml_string) -> dict:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_string)
        user = root.find("user")
        if user is None:
            raise OsmUserInfoException("Nom d'utilisateur non trouvé dans la réponse")
        return {"display_name": user.attrib.get("display_name")}  # type: ignore

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(settings.OSM_USER_DETAIL_URL, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise OsmUserInfoException("Nom d'utilisateur non trouvé")
    return parse_osm_user_info(response.text)


def make_osm_change(access_token, features_to_update: list[dict]):
    oauth_session = OAuth2Session(
        settings.OSM_CLIENT_ID, token={"access_token": access_token}
    )
    api = osmapi.OsmApi(api=settings.OSM_API_URL, session=oauth_session)
    # features_to_update = [feature_to_update]
    with api.Changeset({"comment": "UPDATE RNB FROM OSM DATA"}) as changeset_id:
        for feature in features_to_update:
            osm_id = feature["osm_id"]
            if feature["osm_type"] == OSMFeatureType.WAY.value:
                try:
                    way = api.WayGet(osm_id)
                except (errors.ElementNotFoundApiError, errors.ElementDeletedApiError):
                    raise OsmFeatureUpdateException(f"Way {osm_id} not found in OSM")

                existing_tags = way["tag"]
                existing_tags["ref:FR:RNB"] = feature["rnb"]
                if feature.get("diff_rnb", "") != "":
                    existing_tags["diff:ref:FR:RNB"] = feature["diff_rnb"]
                try:
                    way = api.WayUpdate(
                        {
                            "id": osm_id,
                            "version": way["version"],
                            "tag": existing_tags,
                            "nd": way["nd"],
                        }
                    )
                except errors.ChangesetAlreadyOpenError:
                    raise OsmFeatureUpdateException(
                        f"Way {osm_id} already in changeset"
                    )
                except errors.ChangesetClosedApiError:
                    raise OsmFeatureUpdateException(f"Changeset {changeset_id} closed")
            elif feature["osm_type"] == OSMFeatureType.RELATION.value:
                try:
                    relation = api.RelationGet(osm_id)
                except (errors.ElementNotFoundApiError, errors.ElementDeletedApiError):
                    raise OsmFeatureUpdateException(
                        f"Relation {osm_id} not found in OSM"
                    )
                existing_tags = relation["tag"]
                existing_tags["ref:FR:RNB"] = feature["rnb"]
                if feature.get("diff_rnb", "") != "":
                    existing_tags["diff:ref:FR:RNB"] = feature["diff_rnb"]

                try:
                    relation = api.RelationUpdate(
                        {
                            "id": osm_id,
                            "version": relation["version"],
                            "tag": existing_tags,
                            "member": relation["member"],
                        }
                    )
                except errors.ChangesetAlreadyOpenError:
                    raise OsmFeatureUpdateException(
                        f"Relation {osm_id} already in changeset, you can retry"
                    )
                except errors.ChangesetClosedApiError:
                    raise OsmFeatureUpdateException(f"Changeset {changeset_id} closed")
            else:
                raise OsmFeatureUpdateException(
                    f" OSM type {feature['osm_type']} not supported"
                )


def make_local_db_osm_change(features_to_update: list[dict]):
    try:
        for feature_to_update in features_to_update:
            osm_type = feature_to_update["osm_type"]
            if osm_type == OSMFeatureType.WAY.value:
                osm_id = feature_to_update["osm_id"]
            elif osm_type == OSMFeatureType.RELATION.value:
                osm_id = feature_to_update["osm_id"] * -1
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE extracted_buildings SET rnb = %s, diff_rnb = %s WHERE osm_id = %s",
                    [
                        feature_to_update["rnb"],
                        feature_to_update.get("diff_rnb", ""),
                        osm_id,
                    ],
                )
    except Exception as e:
        logger.error(e)
        raise OsmLocalFeatureUpdateException("Error updating feature") from e


def get_osm_parent_building(parent_osm_id: int):
    parent_osm_geometry = f"""
        SELECT  
            st_asgeojson(way) as geometry, 
            COALESCE(tags -> 'ref:FR:RNB', '') as rnb,
            COALESCE(tags -> 'diff:ref:FR:RNB', '') as diff_rnb 
        FROM (
                SELECT
                    osm_id,
                    ST_Transform(way, 4326) as way,
                    tags 
                FROM
                    planet_osm_polygon
            
                UNION
                ALL
                SELECT
                    osm_id,
                    ST_MakePolygon(ST_Transform(way, 4326)) as way,
                    tags
                FROM
                    planet_osm_line
                WHERE
                    ST_IsClosed(way)
                    AND ST_NPoints(way) >= 4
        ) subquery WHERE osm_id = {parent_osm_id};
    """
    building_parent_rnb_sql_query = f"""
        WITH filtered_osm AS (
            SELECT
                osm_id,
                ST_Transform(way, 4326) as way,
                ST_Area(ST_Transform(way, 4326)) as osm_area
            FROM
                planet_osm_polygon
            WHERE
                osm_id = {parent_osm_id}
            UNION
            ALL
            SELECT
                osm_id,
                ST_MakePolygon(ST_Transform(way, 4326)) as way,
                ST_Area(ST_MakePolygon(ST_Transform(way, 4326))) as osm_area
            FROM
                planet_osm_line
            WHERE
                osm_id = {parent_osm_id}
                AND ST_IsClosed(way)
                AND ST_NPoints(way) >= 4
        ),
        paired AS (
            SELECT
                f.osm_id,
                r.rnb_id,
                ST_Area(ST_Intersection(f.way, r.shape)) AS intersect_area,
                f.osm_area,
                ST_Area(r.shape) as rnb_area
            FROM
                filtered_osm AS f
                JOIN rnb_buildings AS r ON r.shape && f.way
                AND ST_Intersects(f.way, r.shape)
            WHERE
                st_isvalid(r.shape)
        ),
        rec70 AS (
            SELECT
                osm_id,
                rnb_id,
                (
                    intersect_area / LEAST(osm_area, rnb_area) * 100.0
                ) AS pct_recouvrement
            FROM
                paired
            WHERE
                intersect_area > 0
                AND (
                    intersect_area / LEAST(osm_area, rnb_area) * 100.0
                ) > 70.0
        ),
        rnb_counts AS (
            SELECT
                rnb_id,
                COUNT(*) AS occurrences
            FROM
                rec70
            GROUP BY
                rnb_id
        ),
        -- 5) Joindre pour pouvoir distinguer 'splited'
        rec_joined AS (
            SELECT
                r.osm_id,
                r.rnb_id,
                r.pct_recouvrement,
                c.occurrences
            FROM
                rec70 AS r
                JOIN rnb_counts AS c USING (rnb_id)
        ),
        agg AS (
            SELECT
                osm_id,
                string_agg(rnb_id :: text, ';') AS match_rnb_ids,
                round(avg(pct_recouvrement)) / 100.0 AS match_rnb_score,
                CASE
                    WHEN COUNT(*) > 1 THEN 'multiple'
                    WHEN MAX(occurrences) > 1 THEN 'splited'
                    ELSE NULL
                END AS match_rnb_diff
            FROM
                rec_joined
            GROUP BY
                osm_id
        )
        SELECT
            *
        FROM
            agg;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(parent_osm_geometry)
            parent_osm_geometry = cursor.fetchone()
            if parent_osm_geometry is not None:
                cols = [col[0] for col in cursor.description]  # type: ignore
                parent_osm_geometry = dict(zip(cols, parent_osm_geometry))

            cursor.execute(building_parent_rnb_sql_query)
            building_parent = cursor.fetchone()
            if building_parent is not None:
                cols = [col[0] for col in cursor.description]  # type: ignore
                building_parent = dict(zip(cols, building_parent))

            return {
                "parent_osm": parent_osm_geometry,  # type: ignore
                "parent_matching_rnb": building_parent,
            }
    except DatabaseError as e:
        raise GetOsmParentBuildingException("Failed to get osm parent building") from e
