from adrf import serializers

from rest_framework.serializers import CharField, HiddenField, CurrentUserDefault

from apps.automation.models import ScheduledJob, JobExecution
from apps.infrastructure.models import Cluster, Node


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        exclude = ["user"]
        read_only_fields = ["id", "created", "updated"]


class NodeSerializer(serializers.ModelSerializer):
    password = CharField(write_only=True, required=True)

    class Meta:
        model = Node
        fields = "__all__"
        read_only_fields = ["id", "created", "updated", "agent_key", "last_seen"]


class ScheduledJobSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = ScheduledJob
        exclude = ["schedule"]
        read_only_fields = ["id", "created", "updated"]


class JobExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobExecution
        fields = "__all__"
        read_only_fields = [
            "id",
            "created",
            "started_at",
            "finished_at",
            "stdout",
            "stderr",
            "exit_code",
        ]
