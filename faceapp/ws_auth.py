import json
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """Autentikasi pengguna WebSocket via query string ?token=<key>."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = scope.get('query_string', b'').decode('utf-8')
        params = parse_qs(query_string)
        token_key = params.get('token', [None])[0]
        scope = dict(scope)
        scope['user'] = AnonymousUser()
        if token_key:
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                scope['user'] = token.user
            except Token.DoesNotExist:
                pass
        await self.inner(scope, receive, send)


def make_middleware_stack(inner):
    return TokenAuthMiddleware(inner)
