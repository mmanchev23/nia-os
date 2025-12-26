from django_q.models import Schedule

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.infrastructure.models import Cluster, Node


class ScheduledJob(BaseModel):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="jobs",
        verbose_name=_("User"),
    )

    node = models.ForeignKey(
        to=Node,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
        verbose_name=_("Node"),
    )

    cluster = models.ForeignKey(
        to=Cluster,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
        verbose_name=_("Cluster"),
    )

    name = models.CharField(max_length=128, verbose_name=_("Name"))

    command = models.TextField(
        help_text=_("Bash command to execute"),
        verbose_name=_("Command"),
    )

    schedule = models.OneToOneField(
        to=Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nia_job",
        verbose_name=_("Schedule"),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Scheduled Job")
        verbose_name_plural = _("Scheduled Jobs")


class JobExecution(BaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        SUCCESS = "SUCCESS", _("Success")
        FAILED = "FAILED", _("Failed")

    job = models.ForeignKey(
        to=ScheduledJob,
        on_delete=models.CASCADE,
        related_name="executions",
        verbose_name=_("Job"),
    )

    node = models.ForeignKey(
        to=Node,
        on_delete=models.CASCADE,
        related_name="job_executions",
        verbose_name=_("Node"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )

    exit_code = models.IntegerField(null=True, blank=True, verbose_name=_("Exit Code"))

    stdout = models.TextField(blank=True, verbose_name=_("Standard Output"))

    stderr = models.TextField(blank=True, verbose_name=_("Standard Error"))

    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Started At"))

    finished_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Finished At")
    )

    class Meta:
        ordering = ["-started_at"]
