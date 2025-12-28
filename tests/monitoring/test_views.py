import json

import pytest

from django.urls import reverse

from apps.monitoring.models import Metric
from apps.infrastructure.models import Node

from tests.factories import NodeFactory


pytestmark = pytest.mark.django_db


class TestMonitoringAPI:
    def test_ingest_metrics_success(self, client) -> None:
        node = NodeFactory()
        url = reverse("metric_ingest")

        payload = {
            "agent_key": str(node.agent_key),
            "cpu_percent": 15.5,
            "ram_percent": 30.0,
            "disk_percent": 45.0,
        }

        response = client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 200
        assert Metric.objects.count() == 1

        node.refresh_from_db()
        assert node.status == Node.Status.ONLINE

    def test_ingest_invalid_key(self, client) -> None:
        url = reverse("metric_ingest")
        import uuid

        payload = {
            "agent_key": str(uuid.uuid4()),
            "cpu_percent": 10,
            "ram_percent": 10,
            "disk_percent": 10,
        }

        response = client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 403
        assert "Invalid Agent Key" in response.json()["error"]

    def test_ingest_invalid_json(self, client) -> None:
        url = reverse("metric_ingest")
        response = client.post(url, data="not json", content_type="application/json")
        assert response.status_code == 400
