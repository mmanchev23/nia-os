import pytest


from unittest.mock import MagicMock

from apps.api.v1.serializers import (
    ClusterSerializer,
    NodeSerializer,
    ScheduledJobSerializer,
)

from tests.factories import UserFactory, ClusterFactory, NodeFactory

pytestmark = pytest.mark.django_db


class TestClusterSerializer:
    def test_serializer_valid_data(self) -> None:
        user = UserFactory()
        data = {"name": "Test Cluster", "summary": "Some info"}
        serializer = ClusterSerializer(data=data, context={"request": None})
        assert serializer.is_valid(), serializer.errors
        cluster = serializer.save(user=user)
        assert cluster.name == "Test Cluster"
        assert cluster.user == user


class TestNodeSerializer:
    def test_node_serializer_hides_password(self) -> None:
        cluster = ClusterFactory()
        data = {
            "cluster": cluster.id,
            "hostname": "web-01",
            "ip_address": "192.168.1.1",
            "username": "admin",
            "password": "secret_password",
        }
        serializer = NodeSerializer(data=data)
        assert serializer.is_valid()
        node = serializer.save()
        representation = NodeSerializer(node).data
        assert "password" not in representation


class TestScheduledJobSerializer:
    def test_job_serializer_valid(self) -> None:
        node = NodeFactory()
        data = {"name": "Backup", "command": "tar -czf ...", "node": node.id}

        request = MagicMock()
        request.user = node.cluster.user

        serializer = ScheduledJobSerializer(data=data, context={"request": request})

        assert serializer.is_valid(), serializer.errors
        job = serializer.save()
        assert job.name == "Backup"
        assert job.user == node.cluster.user
