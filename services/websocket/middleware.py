import os  # noqa: E402

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcda_api_project.settings')  # noqa: E402
import django  # noqa: E402

django.setup()  # noqa: E402
from urllib.parse import parse_qs  # noqa: E402

from channels.db import database_sync_to_async  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402
from rest_framework_simplejwt.tokens import AccessToken  # noqa: E402

User = get_user_model()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = None

        # Check Authorization header first
        for name, value in scope.get('headers', []):
            if name == b"authorization":
                parts = value.decode().split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
                    break

        # If no token in header, check query string
        if token is None:
            query_string = scope.get('query_string', b'').decode()
            params = parse_qs(query_string)
            token_list = params.get('token')
            # Check if list exists and has a non-empty value
            if token_list and token_list[0]:
                token = token_list[0]

        user = AnonymousUser()
        if token:  # Now checking if token string exists and is not empty
            try:
                # Log first 20 chars for debugging
                access = AccessToken(token)
                user_id = access.get('user_id')
                if user_id:
                    user = await get_user_from_id(user_id)
            except Exception as e:
                print(f'Token validation failed: {e}')
                user = AnonymousUser()

        scope['user'] = user
        return await self.app(scope, receive, send)


@database_sync_to_async
def get_user_from_id(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()
