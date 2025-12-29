import json

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required

from apps.infrastructure.models import Cluster, Node
from apps.automation.models import ScheduledJob
from apps.monitoring.models import Metric


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "core/index.html")


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    user = request.user
    user_nodes = Node.objects.filter(cluster__user=user)

    total_nodes = user_nodes.count()
    online_nodes = user_nodes.filter(status=Node.Status.ONLINE).count()
    health_score = int((online_nodes / total_nodes * 100)) if total_nodes > 0 else 0

    context = {
        "stats": {
            "health": health_score,
            "clusters": Cluster.objects.filter(user=user).count(),
            "nodes": total_nodes,
            "online": online_nodes,
            "jobs": ScheduledJob.objects.filter(user=user).count(),
        }
    }

    if (
        request.headers.get("HX-Request")
        and request.headers.get("HX-Target") == "stats-container"
    ):
        return render(request, "core/dashboard.html#stats_content", context)

    context["recent_nodes"] = user_nodes.order_by("-last_seen")[:5]
    context["recent_jobs"] = ScheduledJob.objects.filter(user=user).order_by("-id")[:5]

    recent_metrics = Metric.objects.filter(node__in=user_nodes).order_by("-created")[
        :12
    ]

    history = list(reversed(recent_metrics))

    initial_chart_data = {
        "labels": [m.created.strftime("%H:%M:%S") for m in history],
        "cpu": [m.cpu_percent for m in history],
        "memory": [m.ram_percent for m in history],
    }

    if not history:
        initial_chart_data = {
            "labels": [_("Wait..."), _("Wait..."), _("Wait...")],
            "cpu": [0, 0, 0],
            "memory": [0, 0, 0],
        }

    context["initial_chart_data"] = json.dumps(initial_chart_data)

    offline_nodes = total_nodes - online_nodes
    unknown_nodes = total_nodes - (online_nodes + offline_nodes)
    context["status_chart_data"] = json.dumps(
        {"online": online_nodes, "offline": offline_nodes, "unknown": unknown_nodes}
    )

    return render(request, "core/dashboard.html", context)


@login_required
def dashboard_metrics_json(request: HttpRequest) -> JsonResponse:
    user = request.user
    user_nodes = Node.objects.filter(cluster__user=user)

    online = user_nodes.filter(status=Node.Status.ONLINE).count()
    offline = user_nodes.filter(status=Node.Status.OFFLINE).count()
    unknown = user_nodes.count() - (online + offline)

    active_nodes = user_nodes.filter(status=Node.Status.ONLINE)

    total_cpu = 0
    total_mem = 0
    count = 0

    for node in active_nodes:
        last_metric = node.metrics.order_by("-created").first()

        if last_metric:
            total_cpu += last_metric.cpu_percent
            total_mem += last_metric.ram_percent
            count += 1

    avg_cpu = round(total_cpu / count, 1) if count > 0 else 0
    avg_mem = round(total_mem / count, 1) if count > 0 else 0

    return JsonResponse(
        {
            "status": {"online": online, "offline": offline, "unknown": unknown},
            "telemetry": {"cpu": avg_cpu, "memory": avg_mem},
        }
    )
