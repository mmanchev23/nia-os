import json

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .dtos import MetricSubmissionDTO
from .services import MonitoringService


@csrf_exempt
@require_POST
def ingest_metrics(request: HttpRequest) -> HttpResponse:
    try:
        data = json.loads(request.body)
        dto = MetricSubmissionDTO(
            agent_key=data.get("agent_key"),
            cpu_percent=float(data.get("cpu_percent")),
            ram_percent=float(data.get("ram_percent")),
            disk_percent=float(data.get("disk_percent")),
        )
        MonitoringService.ingest_metrics(dto)
        return JsonResponse({"status": "ok"}, status=200)

    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": _("Invalid JSON format")}, status=400)
    except ValidationError:
        return JsonResponse({"error": _("Invalid Agent Key")}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
