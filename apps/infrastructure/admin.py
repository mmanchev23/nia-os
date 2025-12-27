from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Cluster, Node


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "nodes", "created", "updated"]
    list_filter = ["user", "created", "updated"]
    search_fields = [
        "name",
        "summary",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    search_help_text = _("Search by cluster name and summary or user details.")
    autocomplete_fields = ["user"]

    def nodes(self, obj) -> int:
        return obj.nodes.count()

    nodes.short_description = _("Nodes")


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = [
        "hostname",
        "ip_address",
        "cluster",
        "cluster_user",
        "created",
        "updated",
    ]
    list_filter = ["cluster", "cluster__user", "created", "updated"]
    search_fields = [
        "hostname",
        "ip_address",
        "cluster__name",
        "cluster__user__username",
        "cluster__user__email",
        "cluster__user__first_name",
        "cluster__user__last_name",
    ]
    search_help_text = _("Search by node hostname and ip address or cluster details.")
    autocomplete_fields = ["cluster"]

    def cluster_user(self, obj) -> str:
        return obj.cluster.user

    cluster_user.short_description = _("User")
    cluster_user.admin_order_field = "cluster__user"
