from django.shortcuts import get_object_or_404
from group.subModels.icon import Icon
from ..models import (
    Group,
    Layer,
    Layer_provider_style,
    Tags,
)
from typing import List
from rest_framework import permissions, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from geosmBackend.cuserViews import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    MultipleFieldLookupListMixin,
)
from rest_framework import status
from django.conf import settings
from django.db import connection
from django.http.request import QueryDict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..documents import LayerDocument
from ..serializers import (
    GroupSerializer,
    LayerCreateDeserializer,
    LayerSerializer,
    LayerProviderStyleSerializer,
    LayerUpdateDeserializer,
    ListCreateLayerQueryParamsDeserializer,
    SetPrincipalLayerDeserializer,
    TagsSerializer,
)


class GetOldLayer(APIView):
    swagger_schema = None
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        if "layer_id" in request.data:
            key_couche = request.data["layer_id"]
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT layer_id FROM old_layer WHERE key_couche=" + str(key_couche)
                )
                layer_id = cursor.fetchone()[0]
                layer: Layer = Layer.objects.select_related().filter(pk=layer_id).get()

                return Response(
                    {
                        "layer": LayerSerializer(
                            Layer.objects.filter(pk__in=[layer.layer_id]), many=True
                        ).data[0],
                        "group": GroupSerializer(
                            Group.objects.filter(pk__in=[layer.sub.group.group_id]),
                            many=True,
                        ).data[0],
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                "key_couche not present in the request",
                status=status.HTTP_400_BAD_REQUEST,
            )


class RetrieveUpdateDestroyLayerView(RetrieveUpdateDestroyAPIView):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer

    def get_authenticators(self):
        if self.request.method == "GET":
            authentication_classes = []
            return authentication_classes
        else:
            return super(self.__class__, self).get_authenticators()

    def get_permissions(self):
        if self.request.method != "GET":
            self.permission_classes = [permissions.IsAuthenticated]
        return super(self.__class__, self).get_permissions()

    @swagger_auto_schema(
        operation_summary="Update a layer",
        responses={200: LayerSerializer()},
        tags=["Layer"],
    )
    def put(self, request, pk, format=None):
        """update layer"""

        layer = get_object_or_404(Layer.objects.all(), pk=pk)
        deserializer = LayerUpdateDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)
        data: dict = deserializer.validated_data  # type: ignore

        if data.get("svg_as_text", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text"], write_to=fileName, unsafe=True
            )
            dataFile = open(fileName, "rb")
            cercle_icon = File(dataFile)

        if data.get("svg_as_text_square", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text_square"],
                write_to=fileName,
                unsafe=True,
            )
            dataFile = open(fileName, "rb")
            square_icon = File(dataFile)

        if (
            "icon" in request.data
            and data.get("svg_as_text", None) is None
            and data.get("svg_as_text_square", None) is None
        ):
            icon: Icon = Icon.objects.get(pk=request.data["icon"])
            cercle_icon = icon.path
            square_icon = icon.path

        layer.name = data["name"]
        layer.protocol_carto = data["protocol_carto"]
        layer.color = data["color"]
        layer.icon_color = data["icon_color"]
        layer.icon = data["icon"]
        layer.icon_background = data["icon_background"]
        layer.cercle_icon = cercle_icon  # type: ignore
        layer.square_icon = square_icon  # type: ignore

        layer.save()

        return Response(LayerSerializer(layer).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve a layer",
        responses={200: LayerSerializer()},
        tags=["Layer"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a Layer"""
        return super(RetrieveUpdateDestroyLayerView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a layer",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Layer"],
    )
    def delete(self, request, *args, **kwargs):
        """delete a layer"""
        return super(RetrieveUpdateDestroyLayerView, self).delete(
            request, *args, **kwargs
        )


class ListCreateLayerView(ListCreateAPIView):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    permission_classes = []
    authentication_classes = []
    lookup_fields = ["sub", "sub__group", "principal"]
    model = Layer

    @swagger_auto_schema(
        operation_summary="Retrieve all layers",
        responses={200: LayerSerializer(many=True)},
        tags=["Layer"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all layers"""
        query_params_deserializer = ListCreateLayerQueryParamsDeserializer(
            data=self.request.query_params  # type: ignore
        )
        query_params_deserializer.is_valid(raise_exception=True)
        validated_data = query_params_deserializer.validated_data
        queryset = self.get_queryset()
        if validated_data.get("principal", None) is None:
            validated_data.pop("principal")
        print(validated_data, "--" * 99)
        queryset = queryset.filter(**validated_data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        # return queryset
        # return super(ListCreateLayerView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new layer",
        responses={200: LayerSerializer()},
        tags=["Layer"],
    )
    def post(self, request, *args, **kwargs):
        """Create a new layer"""
        deserializer = LayerCreateDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        data: dict = deserializer.validated_data  # type: ignore

        if data.get("svg_as_text", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text"], write_to=fileName, unsafe=True
            )
            dataFile = open(fileName, "rb")
            cercle_icon = File(dataFile)

        if data.get("svg_as_text_square", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text_square"],
                write_to=fileName,
                unsafe=True,
            )
            dataFile = open(fileName, "rb")
            square_icon = File(dataFile)

        if (
            "icon" in request.data
            and data.get("svg_as_text", None) is None
            and data.get("svg_as_text_square", None) is None
        ):
            icon: Icon = Icon.objects.get(pk=request.data["icon"])
            cercle_icon = icon.path
            square_icon = icon.path

        layer = Layer.objects.create(
            name=data["name"],
            protocol_carto=data["protocol_carto"],
            color=data["color"],
            icon_color=data["icon_color"],
            icon=data["icon"],
            icon_background=data["icon_background"],
            cercle_icon=cercle_icon,
            square_icon=square_icon,
            sub=data["sub"],
        )

        return Response(LayerSerializer(layer).data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyLayerProviderStyleView(RetrieveUpdateDestroyAPIView):
    queryset = Layer_provider_style.objects.all()
    serializer_class = LayerProviderStyleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve a relation layerProviderStyle",
        responses={200: LayerProviderStyleSerializer()},
        tags=["Layer-provider-style"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a relation layerProviderStyle"""
        return super(RetrieveUpdateDestroyLayerProviderStyleView, self).get(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="update a relation layerProviderStyle",
        responses={200: LayerProviderStyleSerializer()},
        tags=["Layer-provider-style"],
    )
    def put(self, request, *args, **kwargs):
        """update a relation layerProviderStyle"""
        return super(RetrieveUpdateDestroyLayerProviderStyleView, self).put(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Delete a relation layerProviderStyle",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Layer-provider-style"],
    )
    def delete(self, request, *args, **kwargs):
        """delete a relation layerProviderStyle"""
        return super(RetrieveUpdateDestroyLayerProviderStyleView, self).delete(
            request, *args, **kwargs
        )


class ListCreateLayerProviderStyleView(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset = Layer_provider_style.objects.all()
    serializer_class = LayerProviderStyleSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = Layer_provider_style
    lookup_fields = ["layer_id"]

    @swagger_auto_schema(
        operation_summary="Retrieve all relations layerProviderStyles",
        responses={200: LayerSerializer(many=True)},
        tags=["Layer-provider-style"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all relations layerProviderStyles"""
        return super(ListCreateLayerProviderStyleView, self).get(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Create one relation layerProviderStyle",
        responses={200: LayerSerializer(many=True)},
        tags=["Layer-provider-style"],
    )
    def post(self, request, *args, **kwargs):
        """Create one relation layerProviderStyle"""
        return super(ListCreateLayerProviderStyleView, self).post(
            request, *args, **kwargs
        )


class LayerProviderReorderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Set order of providers in a layer",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reorderProviders": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="The array of all providers of the layer with thier new order",
                    items={
                        "type": openapi.TYPE_OBJECT,
                        "properties": {
                            "id": {
                                "type": openapi.TYPE_INTEGER,
                                "description": "The id of the provider",
                            },
                            "ordre": {"type": openapi.TYPE_INTEGER},
                        },
                    },
                )
            },
        ),
        responses={200: ""},
        tags=["Layer"],
    )
    def post(self, request, *args, **kwargs):

        if "reorderProviders" in request.data:
            reorderProviders = request.data["reorderProviders"]
            for provider in reorderProviders:
                Layer_provider_style.objects.filter(pk=provider["id"]).update(
                    ordre=provider["ordre"]
                )

            return Response([], status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": " the 'reorderProviders' parameters is missing "},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SearchLayerTags(generics.ListAPIView):
    """
    View to search tags
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Tags.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    serializer_class = TagsSerializer

    @swagger_auto_schema(
        operation_summary="Search layer by tags",
        responses={200: TagsSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Layer"],
    )
    def get(self, request, *args, **kwargs):
        return super(SearchLayerTags, self).get(request, *args, **kwargs)


class searchLayer(APIView):

    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Search layer with elasticsearch",
        responses={200: LayerSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Layer"],
    )
    def get(self, request, *args, **kwargs):
        """
        search layer
        """
        searchQuerry = request.GET["search"]
        shouldTags: List = []
        for item in searchQuerry.split():
            shouldTags.append({"match": {"metadata.tags": item}})

        elasticResponse = LayerDocument.search().from_dict(
            {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "boost": 4,
                                    "query": searchQuerry,
                                    "type": "best_fields",
                                    "fuzziness": 2,
                                    "fields": ["name", "name._2gram", "name._3gram"],
                                }
                            },
                            {
                                "nested": {
                                    "path": "metadata",
                                    "query": {"bool": {"should": shouldTags}},
                                }
                            },
                            {
                                "multi_match": {
                                    "query": searchQuerry,
                                    "boost": 0.5,
                                    "fields": ["sub.group", "sub.name"],
                                }
                            },
                        ]
                    }
                }
            }
        )
        pks = []
        for result in elasticResponse:
            if result.meta.index == "layer":
                pks.append(result.meta.id)

        return Response(
            LayerSerializer(Layer.objects.filter(pk__in=pks), many=True).data,
            status=status.HTTP_200_OK,
        )


class SetPrincipalLayer(APIView):
    """Update the principal Layer"""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Define the principal Layer",
        request_body=SetPrincipalLayerDeserializer,
        responses={200: ""},
        tags=["Layer"],
    )
    def post(self, request, pk):
        instance: Layer = get_object_or_404(Layer.objects.all(), pk=pk)

        deserializer = SetPrincipalLayerDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        instance.principal = deserializer.validated_data["principal"]
        instance.save()
        return Response({}, status=status.HTTP_200_OK)
