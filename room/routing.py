from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/(?P<room_name>[\w\u0391-\u03A1\u03B1-\u03C1\u03A3-\u03A9\u03B3-\u03C9-]+)/$", consumers.ChatConsumer.as_asgi()),
]
