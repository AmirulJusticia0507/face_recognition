"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from faceapp.routing import websocket_urlpatterns
from faceapp.ws_auth import make_middleware_stack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    'http': get_asg_application(),
    'websocket': make_middleware_stack(URLRouter(websocket_urlpatterns)),
})
