from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    #re_path(r'', consumers.ChatConsumer.as_asgi()),
    # re_path(r'ws/stream/', consumers.VideoStreamConsumer.as_asgi()),
    path('ws/hand_gesture/', consumers.HandGestureConsumer.as_asgi()),
]
