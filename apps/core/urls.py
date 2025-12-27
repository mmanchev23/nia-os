from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/metrics/",
        views.dashboard_metrics_json,
        name="dashboard_metrics_json",
    ),
]
