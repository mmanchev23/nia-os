import pytest

from tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_user_creation(self) -> None:
        user = UserFactory()

        assert user.pk is not None
        assert len(str(user.pk)) == 36
        assert user.check_password("password123")

    def test_user_string_representation(self) -> None:
        user = UserFactory(username="admin")
        assert str(user) == "admin"
