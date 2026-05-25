import factory

from factory.django import DjangoModelFactory

from apps.monitoring.models import Metric
from apps.automation.models import ScheduledJob, JobExecution
from apps.authentication.models import User
from apps.infrastructure.models import Cluster, Node


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class ClusterFactory(DjangoModelFactory):
    class Meta:
        model = Cluster

    name = factory.Sequence(lambda n: f"Test Cluster {n}")
    user = factory.SubFactory(UserFactory)


class NodeFactory(DjangoModelFactory):
    class Meta:
        model = Node

    hostname = factory.Sequence(lambda n: f"node-{n}")
    ip_address = factory.Faker("ipv4")
    cluster = factory.SubFactory(ClusterFactory)
    password = "encrypted_password_placeholder"


class ScheduledJobFactory(DjangoModelFactory):
    class Meta:
        model = ScheduledJob

    name = factory.Sequence(lambda n: f"Job {n}")
    user = factory.SubFactory(UserFactory)
    node = factory.SubFactory(NodeFactory)
    command = 'echo "hello"'


class JobExecutionFactory(DjangoModelFactory):
    class Meta:
        model = JobExecution

    job = factory.SubFactory(ScheduledJobFactory)
    node = factory.SelfAttribute("job.node")

    status = JobExecution.Status.SUCCESS
    exit_code = 0
    stdout = factory.Faker("text", max_nb_chars=100)
    stderr = ""
    finished_at = factory.Faker("future_datetime")


class MetricFactory(DjangoModelFactory):
    class Meta:
        model = Metric

    node = factory.SubFactory(NodeFactory)
    cpu_percent = factory.Faker("pyfloat", min_value=0, max_value=100, right_digits=2)
    ram_percent = factory.Faker("pyfloat", min_value=0, max_value=100, right_digits=2)
    disk_percent = factory.Faker("pyfloat", min_value=0, max_value=100, right_digits=2)
