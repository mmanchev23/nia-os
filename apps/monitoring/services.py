from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.infrastructure.models import Node

from .models import Metric
from .dtos import MetricSubmissionDTO


class MonitoringService:
    @staticmethod
    def ingest_metrics(data: MetricSubmissionDTO) -> None:
        try:
            node = Node.objects.get(agent_key=data.agent_key)
        except Node.DoesNotExist:
            raise ValidationError("Invalid Agent Key")

        with transaction.atomic():
            if node.status != Node.Status.ONLINE:
                node.status = Node.Status.ONLINE

            node.last_seen = timezone.now()
            node.save(update_fields=["status", "last_seen"])

            Metric.objects.create(
                node=node,
                cpu_percent=data.cpu_percent,
                ram_percent=data.ram_percent,
                disk_percent=data.disk_percent,
            )

    @staticmethod
    def get_latest_metrics(node: Node, limit: int = 30):
        return Metric.objects.filter(node=node).order_by("-created")[:limit]

    @staticmethod
    def prune_old_metrics(days: int = 7):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        Metric.objects.filter(created__lt=cutoff).delete()
