from uuid import uuid7

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False,
        verbose_name=_("ID"),
    )

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created"),
    )

    updated = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("Updated"),
    )

    class Meta:
        abstract = True
        ordering = ["-id"]


class ImmutableBaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False,
        verbose_name=_("ID"),
    )

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created"),
    )

    class Meta:
        abstract = True
        ordering = ["-id"]
