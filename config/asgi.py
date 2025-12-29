"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from config.env import env


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    env.str("DJANGO_SETTINGS_MODULE", "config.settings.deploy"),
)

asgi_application = get_asgi_application()


from channels.auth import AuthMiddlewareStack  # noqa
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from channels.security.websocket import AllowedHostsOriginValidator  # noqa

from apps.infrastructure.routing import websocket_urlpatterns  # noqa


application = ProtocolTypeRouter(
    {
        "http": asgi_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
