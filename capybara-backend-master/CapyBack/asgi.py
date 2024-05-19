"""
ASGI config for CapyBack project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from .consumer import CapyBackConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CapyBack.settings')
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AuthMiddlewareStack(
        URLRouter([
           path('ws/', CapyBackConsumer.as_asgi()),
        ])
    ),
})
