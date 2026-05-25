import pytest

from django.urls import reverse

from apps.automation.models import ScheduledJob

from tests.factories import NodeFactory, ScheduledJobFactory, JobExecutionFactory


pytestmark = pytest.mark.django_db


class TestJobViews:
    def test_job_list(self, client) -> None:
        job = ScheduledJobFactory()
        client.force_login(job.user)
        url = reverse("jobs")

        response = client.get(url)
        assert response.status_code == 200
        assert job.name in response.content.decode()

    def test_job_create_for_node(self, client) -> None:
        node = NodeFactory()
        client.force_login(node.cluster.user)
        url = reverse("job_create")

        data = {
            "name": "Backup Node",
            "command": "tar -czf ...",
            "schedule_type": "O",
            "target_node": node.id,
        }

        headers = {"HTTP_HX_REQUEST": "true"}
        response = client.post(url, data, **headers)

        assert response.status_code == 200
        assert ScheduledJob.objects.count() == 1
        job = ScheduledJob.objects.first()
        assert job.node == node

    def test_job_detail_history_htmx(self, client) -> None:
        job = ScheduledJobFactory()
        client.force_login(job.user)

        JobExecutionFactory.create_batch(20, job=job, node=NodeFactory())

        url = reverse("job", args=[job.id])

        response = client.get(url)
        assert response.status_code == 200

        headers = {"HTTP_HX_REQUEST": "true"}
        response = client.get(url + "?page=2", **headers)

        assert response.status_code == 200
        assert "<tr>" in response.content.decode()
        assert "<html>" not in response.content.decode()
