import datetime
import json
from os.path import join
from pathlib import Path

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from tracking_fields.models import TrackingEvent

from geosmBackend.cuserViews import ListAPIView
from tracking.models import NPSFeedback

from .serializers import (
    CreateNPSFeedbackDeserializer,
    LogRenderTimePerFrameDeserializer,
    TrackingEventSerializer,
)

current_file_path = Path(__file__).resolve().parent


class MultipleFieldLookupListMixin:
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = self.model.objects.all()
        filter = {}
        for field in self.lookup_fields:
            if self.request.query_params.get(field, None):
                filter[field] = self.request.query_params.get(field)
        queryset = queryset.filter(**filter)
        return queryset


class TrackingEventListView(MultipleFieldLookupListMixin, ListAPIView):
    queryset = TrackingEvent.objects.all()
    serializer_class = TrackingEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = TrackingEvent
    lookup_fields = ["object_id"]

    def get(self, request, *args, **kwargs):
        def list(self, request, *args, **kwargs):
            queryset = self.filter_queryset(self.get_queryset())

            if self.request.query_params.get("model_name", None):
                newQueryset = []
                model_name = self.request.query_params.get("model_name")
                for res in queryset:
                    if res.object._meta.model_name == model_name:
                        newQueryset.append(res)
                queryset = newQueryset
            else:
                queryset = []

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return list(self, request, *args, **kwargs)


class LogRenderTimePerFrame(generics.GenericAPIView):
    """
    Log render time per frame to a file, that will be ingest by elasticsearch
    """

    authentication_classes = []

    def post(self, request, *args, **kwargs):
        deserializer = LogRenderTimePerFrameDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        frame_render_time = deserializer.validated_data.get("frame_render_time", [])  # type: ignore
        for frame in frame_render_time:
            frame["layers_names"] = deserializer.validated_data.get("layers_names")
            frame["layers_ids"] = deserializer.validated_data.get("layers_ids")
            frame["extent_size"] = deserializer.validated_data.get("extent_size")
            frame["extent"] = deserializer.validated_data.get("extent")
            frame["current_url"] = deserializer.validated_data.get("current_url")
            frame["response_date_time"] = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        try:
            today = datetime.datetime.now()
            today_str = str(today.day) + "-" + str(today.month) + "-" + str(today.year)
            with open(
                join(current_file_path, "render_time_per_frame_" + today_str + ".log"),
                "a",
            ) as myfile:
                for frame in frame_render_time:
                    myfile.write(json.dumps(frame) + "\n")
        except Exception:
            pass

        return Response(None, status=status.HTTP_200_OK)


class CreateNPSFeedback(generics.GenericAPIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        deserializer = CreateNPSFeedbackDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)
        has_send_no_response = False
        if deserializer.validated_data.get("score", None) is None:
            has_send_no_response = True

        NPSFeedback.objects.create(
            **deserializer.validated_data,  # type: ignore
            has_send_no_response=has_send_no_response,
        )

        return Response(None, status=status.HTTP_200_OK)
