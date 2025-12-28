import pytest

from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.monitoring.services import MonitoringService
from apps.monitoring.models import Metric
from apps.monitoring.dtos import MetricSubmissionDTO
from apps.infrastructure.models import Node

from tests.factories import NodeFactory, MetricFactory


pytestmark = pytest.mark.django_db


class TestMonitoringService:
    def test_ingest_metrics_success(self) -> None:
        node = NodeFactory(status=Node.Status.OFFLINE)

        dto = MetricSubmissionDTO(
            agent_key=node.agent_key,
            cpu_percent=50.0,
            ram_percent=60.0,
            disk_percent=70.0,
        )

        MonitoringService.ingest_metrics(dto)

        assert Metric.objects.count() == 1
        metric = Metric.objects.first()
        assert metric.node == node
        assert metric.cpu_percent == 50.0

        node.refresh_from_db()
        assert node.status == Node.Status.ONLINE
        assert node.last_seen is not None
        assert (timezone.now() - node.last_seen).total_seconds() < 1

    def test_ingest_invalid_key(self) -> None:
        import uuid

        dto = MetricSubmissionDTO(
            agent_key=uuid.uuid4(),
            cpu_percent=1,
            ram_percent=1,
            disk_percent=1,
        )

        with pytest.raises(ValidationError):
            MonitoringService.ingest_metrics(dto)

    def test_prune_old_metrics(self) -> None:
        node = NodeFactory()

        m1 = MetricFactory(node=node)

        old_time = timezone.now() - timedelta(days=8)
        m2 = MetricFactory(node=node)
        Metric.objects.filter(id=m2.id).update(created=old_time)

        assert Metric.objects.count() == 2

        MonitoringService.prune_old_metrics(days=7)

        assert Metric.objects.count() == 1
        assert Metric.objects.first() == m1
