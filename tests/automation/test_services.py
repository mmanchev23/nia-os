import pytest

from django_q.models import Schedule

from apps.automation.services import JobService
from apps.automation.models import ScheduledJob
from apps.automation.dtos import JobDTO

from tests.factories import ClusterFactory, NodeFactory, ScheduledJobFactory


pytestmark = pytest.mark.django_db


class TestJobService:
    def test_create_job_for_node(self) -> None:
        node = NodeFactory()
        user = node.cluster.user

        dto = JobDTO(
            user=user,
            name="Node Backup",
            command="backup.sh",
            schedule_type="O",
            target_type="node",
            target_id=node.id,
        )

        job = JobService.create(dto)

        assert job.node == node
        assert job.cluster is None
        assert job.schedule is not None
        assert Schedule.objects.count() == 1
        assert job.schedule.name == f"NIA-Job-{job.id}"

    def test_create_job_for_cluster(self) -> None:
        cluster = ClusterFactory()
        user = cluster.user

        dto = JobDTO(
            user=user,
            name="Cluster Update",
            command="apt update",
            schedule_type="D",
            target_type="cluster",
            target_id=cluster.id,
            repeats=-1,
        )

        job = JobService.create(dto)
        assert job.cluster == cluster
        assert job.node is None
        assert job.schedule.schedule_type == "D"

    def test_update_job_schedule(self) -> None:
        job = ScheduledJobFactory(name="Old Job", command="echo 1")
        node = NodeFactory()
        dto = JobDTO(node.cluster.user, "Init", "echo 1", "O", "node", node.id)
        job = JobService.create(dto)

        new_dto = JobDTO(
            user=job.user,
            name="New Name",
            command="echo 2",
            schedule_type="H",
            target_type="node",
            target_id=node.id,
            minutes=30,
        )

        updated_job = JobService.update(job.id, job.user, new_dto)

        assert updated_job.name == "New Name"
        assert updated_job.schedule.schedule_type == "H"
        assert updated_job.schedule.minutes == 30

    def test_delete_job_removes_schedule(self) -> None:
        node = NodeFactory()
        dto = JobDTO(node.cluster.user, "Temp", "echo", "O", "node", node.id)
        job = JobService.create(dto)

        schedule_id = job.schedule.id

        JobService.delete(job.id, job.user)

        assert ScheduledJob.objects.count() == 0
        assert Schedule.objects.filter(id=schedule_id).exists() is False
