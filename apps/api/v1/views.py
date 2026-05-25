from adrf import viewsets

from django.db.models import QuerySet

from apps.automation.models import ScheduledJob, JobExecution
from apps.infrastructure.models import Cluster, Node

from .serializers import (
    ScheduledJobSerializer,
    JobExecutionSerializer,
    ClusterSerializer,
    NodeSerializer,
)


class ScheduledJobViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledJobSerializer
    search_fields = ["name", "command"]

    def get_queryset(self) -> QuerySet[ScheduledJob]:
        return ScheduledJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer: ScheduledJobSerializer) -> None:
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: ScheduledJobSerializer) -> None:
        serializer.save(user=self.request.user)


class JobExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = JobExecutionSerializer
    search_fields = ["job__name", "status"]

    def get_queryset(self) -> QuerySet[JobExecution]:
        return JobExecution.objects.filter(job__user=self.request.user)


class ClusterViewSet(viewsets.ModelViewSet):
    serializer_class = ClusterSerializer
    search_fields = ["name", "summary"]

    def get_queryset(self) -> QuerySet[Cluster]:
        return Cluster.objects.filter(user=self.request.user)

    def perform_create(self, serializer: ClusterSerializer) -> None:
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: ClusterSerializer) -> None:
        serializer.save(user=self.request.user)


class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    search_fields = ["hostname", "ip_address", "username"]

    def get_queryset(self) -> QuerySet[Node]:
        return Node.objects.filter(cluster__user=self.request.user)
