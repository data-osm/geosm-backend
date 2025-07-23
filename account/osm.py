import logging

import osmapi
import requests
from django.conf import settings
from django.db import connection, models
from django.http import HttpRequest
from osmapi import errors
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class OSMFeatureType(models.Choices):
    NODE = "node"
    WAY = "way"
    RELATION = "relation"


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


def make_osm_change(access_token, feature_to_update: dict):
    oauth_session = OAuth2Session(
        settings.OSM_CLIENT_ID, token={"access_token": access_token}
    )
    api = osmapi.OsmApi(api=settings.OSM_API_URL, session=oauth_session)
    features_to_update = [feature_to_update]
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


def make_local_db_osm_change(feature_to_update: dict):
    try:
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
        raise OsmLocalFeatureUpdateException("Error updating feature")
