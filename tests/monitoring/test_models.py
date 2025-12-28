import pytest

from tests.factories import MetricFactory


pytestmark = pytest.mark.django_db


class TestMetricModel:
    def test_metric_str(self) -> None:
        metric = MetricFactory()
        assert metric.node.hostname in str(metric)
