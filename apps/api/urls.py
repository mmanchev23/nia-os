from django.urls import path, include

from adrf import routers

from .v1 import views as v1_views


app_name = "api"

router_v1 = routers.DefaultRouter()

router_v1.register(r"jobs", v1_views.ScheduledJobViewSet, basename="job")
router_v1.register(r"executions", v1_views.JobExecutionViewSet, basename="execution")
router_v1.register(r"clusters", v1_views.ClusterViewSet, basename="cluster")
router_v1.register(r"nodes", v1_views.NodeViewSet, basename="node")

urlpatterns = [
    path("v1/", include(router_v1.urls)),
]
