from uuid import UUID

from dataclasses import dataclass

from apps.authentication.models import User


@dataclass(frozen=True)
class JobDTO:
    user: User
    name: str
    command: str
    schedule_type: str
    target_type: str
    target_id: UUID
    minutes: int | None = None
    repeats: int = -1
