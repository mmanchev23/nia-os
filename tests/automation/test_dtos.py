import uuid

import pytest

from dataclasses import FrozenInstanceError

from apps.automation.dtos import JobDTO

from tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestJobDTO:
    def test_init_defaults(self) -> None:
        user = UserFactory()
        target_id = uuid.uuid4()

        dto = JobDTO(
            user=user,
            name="Backup",
            command="tar -czf...",
            schedule_type="O",
            target_type="NODE",
            target_id=target_id,
        )

        assert dto.name == "Backup"
        assert dto.repeats == -1
        assert dto.minutes is None

    def test_immutability(self) -> None:
        user = UserFactory()
        dto = JobDTO(
            user=user,
            name="Backup",
            command="cmd",
            schedule_type="O",
            target_type="NODE",
            target_id=uuid.uuid4(),
        )

        with pytest.raises(FrozenInstanceError):
            dto.command = "rm -rf /"
