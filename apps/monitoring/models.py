from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import ImmutableBaseModel
from apps.infrastructure.models import Node


class Metric(ImmutableBaseModel):
    node = models.ForeignKey(
        to=Node,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name=_("Node"),
    )

    cpu_percent = models.FloatField(verbose_name=_("CPU %"))
    ram_percent = models.FloatField(verbose_name=_("RAM %"))
    disk_percent = models.FloatField(verbose_name=_("Disk %"))

    class Meta:
        verbose_name = _("Metric")
        verbose_name_plural = _("Metrics")
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["node", "-created"]),
        ]

    def __str__(self) -> str:
        return f"{self.node.hostname} - {self.created.strftime('%H:%M:%S')}"
