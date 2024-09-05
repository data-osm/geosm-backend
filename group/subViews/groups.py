from group.subModels.icon import Icon
from ..models import (
    Group,
    Sub,
)
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from geosmBackend.cuserViews import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
    MultipleFieldLookupListMixin,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http.request import QueryDict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import (
    SubWithGroupSerializer,
    MapSerializer,
    GroupSerializer,
    SubSerializer,
    SubWithLayersSerializer,
)


class UpdateOrderGroup(APIView):

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update the order of groups",
        responses={200: "this should not crash (response object with no schema)"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reorderGroups": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="The array of all groups with thier new order",
                    items={
                        "type": openapi.TYPE_OBJECT,
                        "properties": {
                            "group_id": {"type": openapi.TYPE_INTEGER},
                            "order": {"type": openapi.TYPE_INTEGER},
                        },
                    },
                )
            },
        ),
        tags=["Group"],
    )
    def post(self, request, *args, **kwargs):
        """Update the order of group"""
        if "reorderGroups" in request.data:
            reorderGroups = request.data["reorderGroups"]
            for group in reorderGroups:
                Group.objects.filter(pk=group["group_id"]).update(order=group["order"])

            return Response([], status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": " the 'reorderGroups' parameters is missing "},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RetrieveUpdateDestroyGroupView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update a group",
        responses={200: GroupSerializer()},
        tags=["Group"],
    )
    def put(self, request, pk):
        """update a new group"""
        group = get_object_or_404(Group.objects.all(), pk=pk)
        vp_serializer = GroupSerializer(instance=group, data=request.data, partial=True)
        query_dict = QueryDict("", mutable=True)
        query_dict.update(self.request.data)
        if query_dict.get("svg_as_text", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text"], write_to=fileName, unsafe=True
            )
            del request.data["svg_as_text"]
            dataFile = open(fileName, "rb")
            request.data["icon_path"] = File(dataFile)

        if "icon_id" in request.data and query_dict.get("svg_as_text", None) is None:
            icon: Icon = Icon.objects.get(pk=request.data["icon_id"])
            request.data["icon_path"] = icon.path
            try:
                del request.data["svg_as_text"]
            except Exception:
                pass

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a group",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Group"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a group"""
        return super(RetrieveUpdateDestroyGroupView, self).delete(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Retrieve a group",
        responses={200: MapSerializer()},
        tags=["Group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a group"""
        return super(RetrieveUpdateDestroyGroupView, self).get(request, *args, **kwargs)


class ListCreateGroupView(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_fields = ["map"]
    model = Group
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Retrieve all groups order by <<order>> property",
        responses={200: MapSerializer(many=True)},
        tags=["Group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all groups order by <<order>> property"""
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.order_by("order")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add a new group",
        responses={200: MapSerializer()},
        tags=["Group"],
    )
    def post(self, request, *args, **kwargs):
        """Add a new group"""
        vp_serializer = GroupSerializer(data=request.data)
        query_dict = QueryDict("", mutable=True)
        query_dict.update(self.request.data)

        if query_dict.get("svg_as_text", None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix=".png")
            fileName = f.name
            svg2png(
                bytestring=request.data["svg_as_text"], write_to=fileName, unsafe=True
            )
            del request.data["svg_as_text"]
            dataFile = open(fileName, "rb")
            request.data["icon_path"] = File(dataFile)

        if "icon_id" in request.data and query_dict.get("svg_as_text", None) is None:
            icon: Icon = Icon.objects.get(pk=request.data["icon_id"])
            request.data["icon_path"] = icon.path
            try:
                del request.data["svg_as_text"]
            except Exception:
                pass

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDestroySubView(RetrieveUpdateDestroyAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a SubGroup",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Sub group"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a SubGroup"""
        return super(RetrieveUpdateDestroySubView, self).delete(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Retrieve a SubGroup",
        responses={200: SubSerializer()},
        tags=["Sub group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a SubGroup"""
        return super(RetrieveUpdateDestroySubView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a SubGroup",
        responses={200: SubSerializer()},
        tags=["Sub group"],
    )
    def put(self, request, *args, **kwargs):
        """Update a SubGroup"""
        return super(RetrieveUpdateDestroySubView, self).put(request, *args, **kwargs)


class RetrieveSubWithGroup(RetrieveAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubWithGroupSerializer
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Retrieve a SubGroup with his parent group",
        responses={200: SubWithGroupSerializer()},
        tags=["Sub group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a SubGroup with his parent group"""
        return super(RetrieveSubWithGroup, self).get(request, *args, **kwargs)


class ListSubWithLayersView(MultipleFieldLookupListMixin, ListAPIView):
    queryset = Sub.objects.order_by("-updated_at")
    serializer_class = SubWithLayersSerializer
    authentication_classes = []
    lookup_fields = ["group_id"]
    model = Sub

    @swagger_auto_schema(
        operation_summary="Retrieve all subGroups with thier children layers",
        responses={200: SubWithLayersSerializer(many=True)},
        tags=["Sub group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all subGroups with thier children layers"""
        return super(ListSubWithLayersView, self).get(request, *args, **kwargs)


class SubViewListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset = Sub.objects.order_by("-updated_at")
    serializer_class = SubSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_fields = ["group_id"]
    model = Sub

    @swagger_auto_schema(
        operation_summary="Retrieve all SubGroups",
        responses={200: SubSerializer(many=True)},
        tags=["Sub group"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all SubGroups"""
        return super(SubViewListCreate, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new subGroup",
        responses={200: SubSerializer()},
        tags=["Sub group"],
    )
    def post(self, request, *args, **kwargs):
        """Create a new subGroup"""
        return super(SubViewListCreate, self).post(request, *args, **kwargs)
