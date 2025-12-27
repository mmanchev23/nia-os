from django.urls import path

from . import views


urlpatterns = [
    path("api/ingest/", views.ingest_metrics, name="metric_ingest"),
]
