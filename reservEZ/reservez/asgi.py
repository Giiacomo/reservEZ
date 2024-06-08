# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import accounts.socket.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservez.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            accounts.socket.routing.websocket_urlpatterns  # Make sure to import correct routing module
        )
    ),
})
