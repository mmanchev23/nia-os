import pytest

from dataclasses import FrozenInstanceError

from apps.infrastructure.dtos import ClusterDTO, NodeDTO

from tests.factories import UserFactory, ClusterFactory


pytestmark = pytest.mark.django_db


class TestClusterDTO:
    def test_init(self) -> None:
        user = UserFactory()
        dto = ClusterDTO(user=user, name="Prod", summary="Production Cluster")

        assert dto.user == user
        assert dto.name == "Prod"
        assert dto.summary == "Production Cluster"

    def test_immutability(self) -> None:
        """Test that attributes cannot be changed after creation."""
        user = UserFactory()
        dto = ClusterDTO(user=user, name="Prod")

        with pytest.raises(FrozenInstanceError):
            dto.name = "Staging"


class TestNodeDTO:
    def test_init(self) -> None:
        cluster = ClusterFactory()
        dto = NodeDTO(
            cluster=cluster,
            hostname="web-01",
            ip_address="10.0.0.1",
            username="root",
            password="securepassword",
            port=22,
        )

        assert dto.cluster == cluster
        assert dto.hostname == "web-01"
        assert dto.port == 22

    def test_immutability(self) -> None:
        cluster = ClusterFactory()
        dto = NodeDTO(
            cluster=cluster,
            hostname="web-01",
            ip_address="10.0.0.1",
            username="root",
            password="pw",
            port=22,
        )

        with pytest.raises(FrozenInstanceError):
            dto.hostname = "hacked-node"
