from django.urls import path

from . import views


urlpatterns = [
    path("clusters/", views.clusters, name="clusters"),
    path("clusters/create/", views.cluster_create, name="cluster_create"),
    path("clusters/<uuid:cluster_id>/", views.cluster, name="cluster"),
    path(
        "clusters/<uuid:cluster_id>/update/",
        views.cluster_update,
        name="cluster_update",
    ),
    path(
        "clusters/<uuid:cluster_id>/delete/",
        views.cluster_delete,
        name="cluster_delete",
    ),
    path("nodes/", views.nodes, name="nodes"),
    path("nodes/create/", views.node_create, name="node_create"),
    path("nodes/<uuid:node_id>/", views.node, name="node"),
    path("nodes/<uuid:node_id>/update/", views.node_update, name="node_update"),
    path("nodes/<uuid:node_id>/delete/", views.node_delete, name="node_delete"),
    path("nodes/<uuid:node_id>/terminal/", views.terminal, name="terminal"),
    path(
        "node_bulk_upload/<uuid:cluster_id>/",
        views.node_bulk_upload,
        name="node_bulk_upload",
    ),
]
