import pytest

from django.db import IntegrityError

from tests.factories import ClusterFactory, NodeFactory


pytestmark = pytest.mark.django_db


class TestClusterModel:
    def test_cluster_str(self) -> None:
        cluster = ClusterFactory(name="Production")
        assert str(cluster) == "Production"

    def test_unique_cluster_name_per_user(self) -> None:
        cluster1 = ClusterFactory(name="Alpha")
        user = cluster1.user

        with pytest.raises(IntegrityError):
            ClusterFactory(name="Alpha", user=user)

    def test_same_cluster_name_different_users(self) -> None:
        c1 = ClusterFactory(name="Alpha")
        c2 = ClusterFactory(name="Alpha")

        assert c1.user != c2.user
        assert c1.name == c2.name


class TestNodeModel:
    def test_node_str(self) -> None:
        node = NodeFactory(hostname="web-01")
        assert str(node) == "web-01"

    def test_agent_key_generation(self) -> None:
        node = NodeFactory()
        assert node.agent_key is not None
        assert len(str(node.agent_key)) == 36

    def test_unique_hostname_per_cluster(self) -> None:
        cluster = ClusterFactory()
        NodeFactory(cluster=cluster, hostname="web-01")

        with pytest.raises(IntegrityError):
            NodeFactory(cluster=cluster, hostname="web-01")

    def test_unique_ip_per_cluster(self) -> None:
        cluster = ClusterFactory()
        NodeFactory(cluster=cluster, ip_address="192.168.1.5")

        with pytest.raises(IntegrityError):
            NodeFactory(cluster=cluster, ip_address="192.168.1.5")
