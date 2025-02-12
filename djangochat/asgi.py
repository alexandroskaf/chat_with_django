import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat.settings')

import django
django.setup()  # Move this before importing anything Django-related

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import room.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(room.routing.websocket_urlpatterns))
    )
})
