# fmt: off
# isort: skip_file
import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcda_api_project.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from django.core.asgi import get_asgi_application # noqa: E402

from apps.Relationships.routing import websocket_urlpatterns # noqa: E402
from apps.Relationships.middleware import TokenAuthMiddleware  # noqa: E402


application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": TokenAuthMiddleware(
        AllowedHostsOriginValidator(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
