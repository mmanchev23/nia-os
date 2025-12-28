import pytest

from django.urls import reverse

from tests.factories import UserFactory, NodeFactory, ClusterFactory, MetricFactory


pytestmark = pytest.mark.django_db


class TestDashboardView:
    def test_dashboard_stats(self, client) -> None:
        user = UserFactory()
        client.force_login(user)

        c = ClusterFactory(user=user)
        NodeFactory(cluster=c, status="ONLINE")
        NodeFactory(cluster=c, status="OFFLINE")

        url = reverse("dashboard")
        response = client.get(url)

        assert response.status_code == 200

        stats = response.context["stats"]
        assert stats["nodes"] == 2
        assert stats["online"] == 1
        assert stats["health"] == 50

    def test_dashboard_metrics_json(self, client) -> None:
        user = UserFactory()
        client.force_login(user)
        c = ClusterFactory(user=user)
        n = NodeFactory(cluster=c, status="ONLINE")
        MetricFactory(node=n, cpu_percent=50.0, ram_percent=60.0)

        url = reverse("dashboard_metrics_json")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        assert data["status"]["online"] == 1
        assert data["telemetry"]["cpu"] == 50.0
