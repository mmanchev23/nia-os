from django.contrib import admin

from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ["node", "cpu_percent", "ram_percent", "disk_percent", "created"]
    list_filter = ["node", "created"]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
