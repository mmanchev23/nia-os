from django.urls import path

from . import views


urlpatterns = [
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/create/", views.job_create, name="job_create"),
    path("jobs/<uuid:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<uuid:job_id>/update/", views.job_update, name="job_update"),
    path("jobs/<uuid:job_id>/delete/", views.job_delete, name="job_delete"),
]
