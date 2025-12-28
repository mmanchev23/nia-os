import pytest

from django.core.exceptions import ValidationError

from apps.infrastructure.services import ClusterService, NodeService
from apps.infrastructure.models import Cluster, Node
from apps.infrastructure.dtos import ClusterDTO, NodeDTO

from tests.factories import UserFactory, ClusterFactory, NodeFactory


pytestmark = pytest.mark.django_db


class TestClusterService:
    def test_create_cluster(self) -> None:
        user = UserFactory()
        dto = ClusterDTO(user=user, name="Prod", summary="Main")

        cluster = ClusterService.create(dto)

        assert cluster.pk is not None
        assert cluster.name == "Prod"
        assert cluster.user == user

    def test_create_duplicate_cluster_name_fails(self) -> None:
        user = UserFactory()
        ClusterFactory(user=user, name="Prod")

        dto = ClusterDTO(user=user, name="Prod", summary="Duplicate")

        with pytest.raises(ValidationError):
            ClusterService.create(dto)

    def test_list_clusters_permissions(self) -> None:
        user1 = UserFactory()
        user2 = UserFactory()

        c1 = ClusterFactory(user=user1)
        ClusterFactory(user=user2)

        clusters = ClusterService.list(user1)
        assert clusters.count() == 1
        assert clusters.first() == c1

    def test_update_cluster(self) -> None:
        cluster = ClusterFactory(name="Old Name")
        dto = ClusterDTO(user=cluster.user, name="New Name", summary="Updated")

        updated = ClusterService.update(cluster.id, dto)
        assert updated.name == "New Name"

    def test_delete_cluster_success(self) -> None:
        cluster = ClusterFactory()
        ClusterService.delete(cluster.id, cluster.user)
        assert Cluster.objects.count() == 0

    def test_delete_cluster_not_owner(self) -> None:
        cluster = ClusterFactory()
        other_user = UserFactory()

        with pytest.raises(Cluster.DoesNotExist):
            ClusterService.delete(cluster.id, other_user)

        assert Cluster.objects.count() == 1


class TestNodeService:
    def test_create_node(self) -> None:
        cluster = ClusterFactory()
        dto = NodeDTO(
            cluster=cluster,
            hostname="web-01",
            ip_address="10.0.0.50",
            username="root",
            password="password",
            port=22,
        )

        node = NodeService.create(dto)
        assert node.pk is not None
        assert node.cluster == cluster

    def test_list_nodes_filtering(self) -> None:
        cluster = ClusterFactory()
        node1 = NodeFactory(cluster=cluster)
        cluster2 = ClusterFactory(user=cluster.user)
        node2 = NodeFactory(cluster=cluster2)  # noqa

        NodeFactory()

        all_nodes = NodeService.list(cluster.user)
        assert all_nodes.count() == 2

        cluster_nodes = NodeService.list(cluster.user, cluster=cluster)
        assert cluster_nodes.count() == 1
        assert cluster_nodes.first() == node1

    def test_update_node_ownership_check(self) -> None:
        node = NodeFactory()
        hacker = UserFactory()
        hacker_cluster = ClusterFactory(user=hacker)

        dto = NodeDTO(
            cluster=hacker_cluster,
            hostname="moved",
            ip_address="1.1.1.1",
            username="u",
            password="p",
            port=22,
        )

        with pytest.raises(ValueError):
            NodeService.update(node.id, node.cluster.user, dto)

    def test_delete_node(self) -> None:
        node = NodeFactory()
        NodeService.delete(node.id, node.cluster.user)
        assert Node.objects.count() == 0
