from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from django_q.tasks import schedule as create_dq_schedule

from apps.infrastructure.models import Cluster, Node

from .models import ScheduledJob
from .dtos import JobDTO


class JobService:
    @staticmethod
    def create(data: JobDTO) -> ScheduledJob:
        target_node = None
        target_cluster = None

        if data.target_type == "node":
            target_node = Node.objects.get(id=data.target_id, cluster__user=data.user)
        elif data.target_type == "cluster":
            target_cluster = Cluster.objects.get(id=data.target_id, user=data.user)
        else:
            raise ValueError("Invalid target type")

        with transaction.atomic():
            job = ScheduledJob.objects.create(
                name=data.name,
                command=data.command,
                node=target_node,
                cluster=target_cluster,
                user=data.user,
            )

            schedule = create_dq_schedule(
                "apps.automation.tasks.execute_job",
                str(job.id),
                schedule_type=data.schedule_type,
                minutes=data.minutes,
                repeats=data.repeats,
                name=f"NIA-Job-{job.id}",
            )

            job.schedule = schedule
            job.save()

            return job

    @staticmethod
    def list(user) -> QuerySet[ScheduledJob]:
        return ScheduledJob.objects.filter(user=user).select_related("schedule")

    @staticmethod
    def update(job_id: UUID, user, data: JobDTO) -> ScheduledJob:
        with transaction.atomic():
            job = ScheduledJob.objects.select_related("schedule").get(
                id=job_id, user=user
            )

            job.name = data.name
            job.command = data.command

            if data.target_type == "node":
                job.node = Node.objects.get(id=data.target_id)
                job.cluster = None
            else:
                job.cluster = Cluster.objects.get(id=data.target_id)
                job.node = None

            job.save()

            if job.schedule:
                job.schedule.func = "apps.automation.tasks.execute_job"
                job.schedule.args = str((str(job.id),))
                job.schedule.schedule_type = data.schedule_type
                job.schedule.minutes = data.minutes
                job.schedule.repeats = data.repeats
                job.schedule.save()
            else:
                schedule = create_dq_schedule(
                    "apps.automation.tasks.execute_job",
                    str(job.id),
                    schedule_type=data.schedule_type,
                    minutes=data.minutes,
                    repeats=data.repeats,
                    name=f"NIA-Job-{job.id}",
                )
                job.schedule = schedule
                job.save()

            return job

    @staticmethod
    def delete(job_id: UUID, user) -> None:
        try:
            job = ScheduledJob.objects.get(id=job_id, user=user)

            if job.schedule:
                job.schedule.delete()

            job.delete()
        except ScheduledJob.DoesNotExist:
            pass
