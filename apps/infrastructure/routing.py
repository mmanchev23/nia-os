from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path(
        "ws/infrastructure/nodes/<uuid:node_id>/terminal/",
        consumers.NodeTerminalConsumer.as_asgi(),
        name="node_terminal",
    ),
]
