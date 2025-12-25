from dataclasses import dataclass

from apps.authentication.models import User

from .models import Cluster


@dataclass(frozen=True)
class ClusterDTO:
    user: User
    name: str
    summary: str | None = None


@dataclass(frozen=True)
class NodeDTO:
    cluster: Cluster
    hostname: str
    ip_address: str
    username: str
    password: str
    port: int
