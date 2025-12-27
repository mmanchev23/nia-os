from uuid import UUID

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSubmissionDTO:
    agent_key: UUID
    cpu_percent: float
    ram_percent: float
    disk_percent: float
