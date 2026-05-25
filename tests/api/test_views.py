import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import (
    UserFactory,
    ClusterFactory,
    NodeFactory,
    ScheduledJobFactory,
    JobExecutionFactory,
)


pytestmark = pytest.mark.django_db


class TestClusterViewSet:
    def test_list_clusters(self, api_client) -> None:
        user = UserFactory()
        ClusterFactory.create_batch(3, user=user)

        api_client.force_authenticate(user=user)

        url = reverse("api:cluster-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_create_cluster_unauthorized(self, api_client) -> None:
        url = reverse("api:cluster-list")
        data = {"name": "Forbidden"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobViewSet:
    def test_list_jobs_for_user(self, api_client) -> None:
        user = UserFactory()
        ScheduledJobFactory.create_batch(2, user=user)
        api_client.force_authenticate(user=user)

        url = reverse("api:job-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_create_job_auto_assigns_user(self, api_client) -> None:
        user = UserFactory()
        cluster = ClusterFactory(user=user)
        node = NodeFactory(cluster=cluster)
        api_client.force_authenticate(user=user)

        url = reverse("api:job-list")
        data = {"name": "Deploy", "command": "git pull", "node": node.id}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Deploy"


class TestNodeViewSet:
    def test_node_search(self, api_client) -> None:
        user = UserFactory()
        cluster = ClusterFactory(user=user)
        NodeFactory(hostname="prod-web", cluster=cluster)
        NodeFactory(hostname="dev-web", cluster=cluster)

        api_client.force_authenticate(user=user)
        url = reverse("api:node-list")

        response = api_client.get(url, {"search": "prod"})
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["hostname"] == "prod-web"

    def test_create_node_unauthorized(self, api_client) -> None:
        url = reverse("api:node-list")
        data = {"name": "Forbidden"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobExecutionViewSet:
    def test_execution_list_security(self, api_client) -> None:
        user1 = UserFactory()
        job1 = ScheduledJobFactory(user=user1)

        JobExecutionFactory(job=job1)

        api_client.force_authenticate(user=user1)
        url = reverse("api:execution-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
