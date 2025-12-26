import asyncio
import asyncssh

from uuid import UUID

from django.utils import timezone

from apps.infrastructure.models import Node

from .models import ScheduledJob, JobExecution


async def _run_ssh_command(job: ScheduledJob, node: Node) -> None:
    execution = await JobExecution.objects.acreate(
        job=job, node=node, status=JobExecution.Status.PENDING
    )

    try:
        async with asyncssh.connect(
            node.ip_address,
            port=node.port,
            username=node.username,
            password=node.password,
            known_hosts=None,
            connect_timeout=10,
        ) as conn:
            final_command = job.command

            if job.command.strip().startswith("sudo"):
                final_command = (
                    f"echo '{node.password}' | sudo -S -p '' {job.command[5:]}"
                )

            result = await conn.run(final_command)

            execution.stdout = result.stdout
            execution.stderr = result.stderr
            execution.exit_code = result.exit_status

            if result.exit_status == 0:
                execution.status = JobExecution.Status.SUCCESS
            else:
                execution.status = JobExecution.Status.FAILED

    except Exception as e:
        execution.stderr = f"SSH Connection Failed: {str(e)}"
        execution.status = JobExecution.Status.FAILED

    execution.finished_at = timezone.now()
    await execution.asave()


async def _run_batch(job, targets) -> None:
    tasks = [_run_ssh_command(job, node) for node in targets]
    await asyncio.gather(*tasks)


def execute_job(job_id: UUID) -> None:
    try:
        job = (
            ScheduledJob.objects.select_related("node", "cluster")
            .prefetch_related("cluster__nodes")
            .get(id=job_id)
        )
    except ScheduledJob.DoesNotExist:
        return

    targets = []

    if job.node:
        targets.append(job.node)
    elif job.cluster:
        targets.extend(job.cluster.nodes.all())

    if not targets:
        return

    asyncio.run(_run_batch(job, targets))
