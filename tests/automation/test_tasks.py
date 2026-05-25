import pytest

from unittest.mock import patch, MagicMock, AsyncMock

from apps.automation.tasks import execute_job
from apps.automation.models import JobExecution

from tests.factories import ScheduledJobFactory, NodeFactory, ClusterFactory


pytestmark = pytest.mark.django_db


@pytest.mark.django_db(transaction=True)
@patch("apps.automation.tasks.asyncssh.connect")
def test_execute_job_success(mock_connect) -> None:
    node = NodeFactory(password="secret")
    job = ScheduledJobFactory(node=node, command="echo 'hello'")

    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.stdout = "hello output"
    mock_result.stderr = ""
    mock_result.exit_status = 0
    mock_conn.run = AsyncMock(return_value=mock_result)
    mock_connect.return_value.__aenter__.return_value = mock_conn
    execute_job(str(job.id))

    mock_connect.assert_called_with(
        node.ip_address,
        port=node.port,
        username=node.username,
        password=node.password,
        known_hosts=None,
        client_keys=None,
        config=None,
        connect_timeout=10,
    )

    mock_conn.run.assert_awaited_with(job.command)

    execution = JobExecution.objects.first()
    assert execution is not None
    assert execution.status == "SUCCESS"
    assert "hello output" in execution.stdout
    assert execution.exit_code == 0
    assert execution.finished_at is not None


@pytest.mark.django_db(transaction=True)
@patch("apps.automation.tasks.asyncssh.connect")
def test_execute_job_connection_failure(mock_connect) -> None:
    node = NodeFactory()
    job = ScheduledJobFactory(node=node)

    mock_connect.return_value.__aenter__.side_effect = Exception("Connection Timeout")

    execute_job(str(job.id))

    execution = JobExecution.objects.first()
    assert execution.status == "FAILED"
    assert "SSH Connection Failed" in execution.stderr
    assert "Connection Timeout" in execution.stderr


@pytest.mark.django_db(transaction=True)
@patch("apps.automation.tasks.asyncssh.connect")
def test_execute_cluster_batch(mock_connect) -> None:
    cluster = ClusterFactory()
    n1 = NodeFactory(cluster=cluster, hostname="node-1")
    n2 = NodeFactory(cluster=cluster, hostname="node-2")

    job = ScheduledJobFactory(cluster=cluster, node=None, command="uptime")

    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.stdout = "up 1 day"
    mock_result.stderr = ""
    mock_result.exit_status = 0

    mock_conn.run = AsyncMock(return_value=mock_result)
    mock_connect.return_value.__aenter__.return_value = mock_conn

    execute_job(str(job.id))

    assert JobExecution.objects.count() == 2

    ex1 = JobExecution.objects.get(node=n1)
    ex2 = JobExecution.objects.get(node=n2)

    assert ex1.status == "SUCCESS"
    assert ex2.status == "SUCCESS"
