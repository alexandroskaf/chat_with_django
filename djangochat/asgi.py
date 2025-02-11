

import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat.settings')

# Set up Django
django.setup()

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
import room.routing
import logging
logger = logging.getLogger(__name__)



async def custom_websocket_handler(scope, receive, send):
    try:
        # Try to handle the connection
        await AuthMiddlewareStack(URLRouter(room.routing.websocket_urlpatterns)).__call__(scope, receive, send)
    except Exception as e:
        # Log the error but don't disrupt the connection
        logger.error(f"WebSocket error: {str(e)}")
        await send({
            'type': 'websocket.close',
            'code': 1000  # A graceful close code (you could use any code depending on your needs)
        })

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(custom_websocket_handler)
})



