import uuid

import pytest

from dataclasses import FrozenInstanceError

from apps.monitoring.dtos import MetricSubmissionDTO


class TestMetricSubmissionDTO:
    def test_init(self) -> None:
        key = uuid.uuid4()
        dto = MetricSubmissionDTO(
            agent_key=key, cpu_percent=45.5, ram_percent=60.2, disk_percent=80.0
        )

        assert dto.agent_key == key
        assert dto.cpu_percent == 45.5
        assert isinstance(dto.disk_percent, float)

    def test_immutability(self) -> None:
        dto = MetricSubmissionDTO(
            agent_key=uuid.uuid4(),
            cpu_percent=10.0,
            ram_percent=10.0,
            disk_percent=10.0,
        )

        with pytest.raises(FrozenInstanceError):
            dto.cpu_percent = 100.0
