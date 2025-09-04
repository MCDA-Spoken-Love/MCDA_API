# fmt: off
# isort: skip_file
import os

import django

from services.websocket.middleware import TokenAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcda_api_project.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from django.core.asgi import get_asgi_application # noqa: E402

from apps.Relationships.routing import relationship_ws_urlpatterns # noqa: E402
from apps.Chat.routing import chat_ws_urlpatterns # noqa: E402

ws_urls = relationship_ws_urlpatterns + chat_ws_urlpatterns

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": TokenAuthMiddleware(
        AllowedHostsOriginValidator(
            URLRouter(ws_urls)
        )
    ),
})
