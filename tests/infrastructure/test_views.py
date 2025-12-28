import pytest

from django.urls import reverse

from apps.infrastructure.models import Cluster, Node

from tests.factories import UserFactory, ClusterFactory, NodeFactory


pytestmark = pytest.mark.django_db


class TestClusterViews:
    def test_list_clusters_anonymous(self, client) -> None:
        url = reverse("clusters")
        response = client.get(url)
        assert response.status_code == 302

    def test_list_clusters_htmx_search(self, client) -> None:
        user = UserFactory()
        client.force_login(user)
        c1 = ClusterFactory(user=user, name="Alpha")  # noqa
        c2 = ClusterFactory(user=user, name="Beta")  # noqa

        url = reverse("clusters")

        response = client.get(url)
        assert response.status_code == 200
        assert "Alpha" in response.content.decode()
        assert "<html" in response.content.decode()

        headers = {"HTTP_HX_REQUEST": "true"}
        response = client.get(url + "?q=Alpha", **headers)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Alpha" in content
        assert "Beta" not in content
        assert "<html" not in content

    def test_cluster_create_modal(self, client) -> None:
        user = UserFactory()
        client.force_login(user)
        url = reverse("cluster_create")

        headers = {"HTTP_HX_REQUEST": "true", "HTTP_HX_TARGET": "cluster-dialog"}
        response = client.get(url, **headers)

        assert response.status_code == 200
        content = response.content.decode()

        assert "modal-box" in content
        assert "<form" in content

    def test_cluster_create_submission(self, client) -> None:
        user = UserFactory()
        client.force_login(user)
        url = reverse("cluster_create")
        data = {"name": "New Cluster", "summary": "Test"}

        headers = {"HTTP_HX_REQUEST": "true"}
        response = client.post(url, data, **headers)

        assert response.status_code == 200
        assert Cluster.objects.filter(name="New Cluster", user=user).exists()

        assert "closeModal" in response["HX-Trigger"]
        assert "HX-Retarget" in response


class TestNodeViews:
    def test_node_detail(self, client) -> None:
        node = NodeFactory()
        client.force_login(node.cluster.user)
        url = reverse("node", args=[node.id])

        response = client.get(url)
        assert response.status_code == 200
        assert node.hostname in response.content.decode()
        assert "curl -s" in response.content.decode()

    def test_node_create_submission(self, client) -> None:
        user = UserFactory()
        cluster = ClusterFactory(user=user)
        client.force_login(user)

        url = reverse("node_create")
        data = {
            "cluster": cluster.id,
            "hostname": "web-01",
            "ip_address": "192.168.1.100",
            "username": "root",
            "password": "password",
            "port": 22,
        }

        headers = {"HTTP_HX_REQUEST": "true"}
        response = client.post(url, data, **headers)

        assert response.status_code == 200
        assert Node.objects.filter(hostname="web-01").exists()
        assert "closeModal" in response["HX-Trigger"]

    def test_node_delete_htmx(self, client) -> None:
        node = NodeFactory()
        client.force_login(node.cluster.user)
        url = reverse("node_delete", args=[node.id])

        headers = {"HTTP_HX_REQUEST": "true", "HTTP_HX_TARGET": "node-dialog"}
        response = client.get(url, **headers)
        assert response.status_code == 200
        assert "Are you sure" in response.content.decode()

        response = client.delete(url, **headers)
        assert response.status_code == 200
        assert Node.objects.count() == 0
        assert "closeModal" in response["HX-Trigger"]
