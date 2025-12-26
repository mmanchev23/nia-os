from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ScheduledJob, JobExecution


@admin.register(ScheduledJob)
class ScheduledJobAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "get_target", "get_schedule_link", "created"]
    list_filter = ["user", "created"]
    search_fields = ["name", "command", "user__email"]

    def get_target(self, obj) -> str:
        if obj.node:
            return format_html("Node: <strong>{}</strong>", obj.node.hostname)
        elif obj.cluster:
            return format_html("Cluster: <strong>{}</strong>", obj.cluster.name)
        return "-"

    get_target.short_description = _("Target")

    def get_schedule_link(self, obj) -> str:
        if not obj.schedule:
            return _("Run Once / Manual")

        url = reverse("admin:django_q_schedule_change", args=[obj.schedule.id])

        return format_html(
            '<a href="{}" target="_blank">{} (Next: {})</a>',
            url,
            obj.schedule.schedule_type,
            obj.schedule.next_run,
        )

    get_schedule_link.short_description = _("Django-Q Schedule")


@admin.register(JobExecution)
class JobExecutionAdmin(admin.ModelAdmin):
    list_display = ["job", "node", "get_status_display", "started_at", "finished_at"]
    list_filter = ["status", "started_at", "job__user"]
    search_fields = ["job__name", "node__hostname", "stdout", "stderr"]

    readonly_fields = [
        "job",
        "node",
        "stdout",
        "stderr",
        "exit_code",
        "started_at",
        "finished_at",
    ]

    def get_status_display(self, obj) -> str:
        colors = {
            "SUCCESS": "green",
            "FAILED": "red",
            "PENDING": "orange",
        }

        color = colors.get(obj.status, "black")

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    get_status_display.short_description = _("Status")
