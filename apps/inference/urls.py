# apps/inference/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    InferenceRunView,
    InferenceHistoryDetailView,
    InferenceHistoryListView,
    AdminInferenceHistoryViewSet,
)

router = DefaultRouter()
router.register(r"admin/histories", AdminInferenceHistoryViewSet, basename="admin-histories")

urlpatterns = [
    path("run/", InferenceRunView.as_view(), name="inference-run"),
    path("history/", InferenceHistoryListView.as_view(), name="inference-history-list"),
    path("history/<int:pk>/", InferenceHistoryDetailView.as_view(), name="inference-history-detail"),
]

urlpatterns += router.urls
