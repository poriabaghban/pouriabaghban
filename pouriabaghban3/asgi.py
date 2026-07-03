import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pouriabaghban3.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import admin_chat.routing as admin_chat_routing
import message.routing as message_routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            admin_chat_routing.websocket_urlpatterns
            + message_routing.websocket_urlpatterns
        )
    ),
})
