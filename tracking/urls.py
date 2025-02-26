from django.urls import path

from .views import CreateNPSFeedback, LogRenderTimePerFrame, TrackingEventListView

# http://127.0.0.1:8000/api/logs/list?object_id=2&model_name=metadata
urlpatterns = [
    path("list", TrackingEventListView.as_view(), name="tracking"),
    path("log-render-time-per-frame", LogRenderTimePerFrame.as_view(), name="tracking"),
    path("nps", CreateNPSFeedback.as_view(), name="create_nps_feedback"),
]
