from .serializers import TrackingEventSerializer
from tracking_fields.models import TrackingEvent
from geosmBackend.cuserViews import ListAPIView
from rest_framework import permissions
from group.models import Metadata
from rest_framework.response import Response

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
        queryset=self.model.objects.all()
        filter = {}
        for field in self.lookup_fields:
            if self.request.query_params.get(field, None):
                filter[field] = self.request.query_params.get(field)
        queryset = queryset.filter(**filter)
        return queryset

class TrackingEventListView(MultipleFieldLookupListMixin, ListAPIView):
    queryset=TrackingEvent.objects.all()
    serializer_class=TrackingEventSerializer
    # permission_classes=[permissions.IsAuthenticated]
    model = TrackingEvent
    lookup_fields=['object_id']

    def get (self, request, *args, **kwargs):
       
        def list(self, request, *args, **kwargs):
            queryset = self.filter_queryset(self.get_queryset())

            if self.request.query_params.get('model_name', None):
                newQueryset=[]
                model_name = self.request.query_params.get('model_name')
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

