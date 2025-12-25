from django.db import models
from django.utils.translation import gettext_lazy as _

from encrypted_fields import fields

from apps.core.models import BaseModel
from apps.authentication.models import User


class Cluster(BaseModel):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="clusters",
        verbose_name=_("User"),
    )

    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        db_index=True,
        verbose_name=_("Name"),
    )

    summary = models.TextField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name=_("Summary"),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Cluster")
        verbose_name_plural = _("Clusters")


class Node(BaseModel):
    cluster = models.ForeignKey(
        to=Cluster,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name=_("Cluster"),
    )

    hostname = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        db_index=True,
        verbose_name=_("Hostname"),
    )

    ip_address = models.GenericIPAddressField(
        null=False,
        blank=False,
        db_index=True,
        verbose_name=_("IP Address"),
    )

    username = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        verbose_name=_("Username"),
    )

    password = fields.EncryptedCharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name=_("Password"),
    )

    port = models.PositiveIntegerField(
        default=22,
        null=False,
        blank=False,
        verbose_name=_("Port"),
    )

    def __str__(self) -> str:
        return self.hostname

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")
        unique_together = ["cluster", "hostname"]
