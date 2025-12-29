from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from django_q.models import Failure, OrmQ, Schedule, Success

from .models import ScheduledJob, JobExecution


admin.site.unregister(Failure)
admin.site.unregister(OrmQ)
admin.site.unregister(Schedule)
admin.site.unregister(Success)


@admin.register(Failure)
class FailureAdmin(ModelAdmin):
    list_display = ["name", "func", "result", "started", "attempt_count"]
    list_filter = ["name", "started"]
    search_fields = ["name", "func"]
    readonly_fields = ["result", "args", "kwargs"]


@admin.register(OrmQ)
class OrmQAdmin(ModelAdmin):
    list_display = ["key", "lock", "task_id"]
    list_filter = ["key"]


@admin.register(Schedule)
class ScheduleAdmin(ModelAdmin):
    list_display = [
        "id",
        "name",
        "func",
        "schedule_type",
        "repeats",
        "next_run",
        "task",
    ]
    list_filter = ["schedule_type", "next_run"]
    search_fields = ["func", "name"]


@admin.register(Success)
class SuccessAdmin(ModelAdmin):
    list_display = ["name", "func", "started", "stopped", "time_taken"]
    list_filter = ["name", "started"]
    search_fields = ["name", "func"]


@admin.register(ScheduledJob)
class ScheduledJobAdmin(ModelAdmin):
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
class JobExecutionAdmin(ModelAdmin):
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
