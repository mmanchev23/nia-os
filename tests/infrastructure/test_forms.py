import pytest

from apps.infrastructure.forms import NodeForm, ClusterForm

from tests.factories import UserFactory, ClusterFactory


pytestmark = pytest.mark.django_db


class TestClusterForm:
    def test_valid_cluster_form(self) -> None:
        form = ClusterForm(data={"name": "Prod", "summary": "Main"})
        assert form.is_valid()

    def test_missing_name(self) -> None:
        form = ClusterForm(data={"name": "", "summary": "Main"})
        assert not form.is_valid()
        assert "name" in form.errors


class TestNodeForm:
    def test_node_form_valid(self) -> None:
        user = UserFactory()
        cluster = ClusterFactory(user=user)
        form = NodeForm(
            user,
            data={
                "cluster": cluster.id,
                "hostname": "web-01",
                "ip_address": "10.0.0.1",
                "username": "root",
                "password": "safe",
                "port": 22,
            },
        )
        assert form.is_valid()

    def test_node_form_invalid_port(self) -> None:
        user = UserFactory()
        form = NodeForm(user, data={"port": 99999})
        assert not form.is_valid()
        assert "port" in form.errors
