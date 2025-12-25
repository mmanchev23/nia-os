from uuid import UUID

from django.db.models import QuerySet

from apps.authentication.models import User

from .models import Cluster, Node
from .dtos import ClusterDTO, NodeDTO


class ClusterService:
    @staticmethod
    def create(data: ClusterDTO) -> Cluster:
        cluster = Cluster(
            user=data.user,
            name=data.name,
            summary=data.summary,
        )
        cluster.full_clean()
        cluster.save()
        return cluster

    @staticmethod
    def list(user: User) -> QuerySet[Cluster]:
        return Cluster.objects.filter(user=user)

    @staticmethod
    def get(cluster_id: UUID, user: User) -> Cluster:
        return Cluster.objects.get(id=cluster_id, user=user)

    @staticmethod
    def update(cluster_id: UUID, data: ClusterDTO) -> Cluster:
        cluster = Cluster.objects.get(id=cluster_id, user=data.user)

        cluster.name = data.name
        cluster.summary = data.summary

        cluster.full_clean()
        cluster.save()
        return cluster

    @staticmethod
    def delete(cluster_id: UUID, user: User) -> None:
        deleted, _ = Cluster.objects.filter(id=cluster_id, user=user).delete()

        if deleted == 0:
            raise Cluster.DoesNotExist("Cluster not found")


class NodeService:
    @staticmethod
    def create(data: NodeDTO) -> Node:
        node = Node(
            cluster=data.cluster,
            hostname=data.hostname,
            ip_address=data.ip_address,
            username=data.username,
            password=data.password,
            port=data.port,
        )
        node.full_clean()
        node.save()
        return node

    @staticmethod
    def list(user: User, cluster: Cluster = None) -> QuerySet[Node]:
        nodes = Node.objects.filter(cluster__user=user)

        if cluster:
            return nodes.filter(cluster=cluster)

        return nodes

    @staticmethod
    def get(node_id: UUID, user: User) -> Node:
        return Node.objects.get(id=node_id, cluster__user=user)

    @staticmethod
    def update(node_id: UUID, user: User, data: NodeDTO) -> Node:
        node = Node.objects.get(id=node_id, cluster__user=user)

        if data.cluster.user != user:
            raise ValueError("Cannot move node to a cluster you do not own")

        node.cluster = data.cluster
        node.hostname = data.hostname
        node.ip_address = data.ip_address
        node.username = data.username
        node.password = data.password
        node.port = data.port

        node.full_clean()
        node.save()
        return node

    @staticmethod
    def delete(node_id: UUID, user: User) -> None:
        deleted, _ = Node.objects.filter(id=node_id, cluster__user=user).delete()

        if deleted == 0:
            raise Node.DoesNotExist("Node not found")
