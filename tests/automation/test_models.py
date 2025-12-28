import pytest

from apps.automation.models import JobExecution

from tests.factories import JobFactory, JobExecutionFactory


pytestmark = pytest.mark.django_db


class TestJobModel:
    def test_job_str(self) -> None:
        job = JobFactory(name="Backup DB")
        assert str(job) == "Backup DB"


class TestJobExecutionModel:
    def test_execution_defaults(self) -> None:
        exec_entry = JobExecutionFactory(status=JobExecution.Status.PENDING)
        assert exec_entry.status == "PENDING"
