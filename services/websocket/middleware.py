import os  # noqa: E402

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcda_api_project.settings')  # noqa: E402
import django  # noqa: E402

django.setup()  # noqa: E402
from urllib.parse import parse_qs  # noqa: E402

from channels.db import database_sync_to_async  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_key = params.get('token')
        if token_key:
            scope['user'] = await self.get_user(token_key[0])
        else:
            scope['user'] = AnonymousUser()
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            user = Token.objects.get(key=token_key).user
            return user

        except Token.DoesNotExist:
            return AnonymousUser()
