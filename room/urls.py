from django.urls import path, re_path
from .views import rooms, room, create_room

from django.urls import path, re_path
from .views import rooms, room, create_room

urlpatterns = [
    path('', rooms, name='rooms'),  # List of rooms
    path('rooms/create/', create_room, name='create_room'),
    # URL pattern for individual rooms (Handles Greek and other characters in slug)
    re_path(r'^rooms/(?P<slug>[\w\-]+)/$', room, name='room')
    # path('check-room-name/', check_room_name, name='check_room_name')
]

