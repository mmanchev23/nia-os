from uuid import uuid7

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid7,
        editable=False,
        verbose_name=_("ID"),
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("User")
        verbose_name_plural = _("Users")
