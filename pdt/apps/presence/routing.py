from django.urls import re_path

from . import consumers, help_consumer

websocket_urlpatterns = [
    re_path(r"^ws/presence/$", consumers.PresenceConsumer.as_asgi()),
    re_path(
        r"^ws/help/(?P<help_id>\d+)/$",
        help_consumer.HelpRoomConsumer.as_asgi(),
    ),
]
