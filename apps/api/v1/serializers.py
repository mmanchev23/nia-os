from adrf import serializers

from apps.automation.models import ScheduledJob, JobExecution
from apps.infrastructure.models import Cluster, Node


class ScheduledJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledJob
        exclude = ["user"]


class JobExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobExecution
        fields = "__all__"


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        exclude = ["user"]


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = "__all__"
