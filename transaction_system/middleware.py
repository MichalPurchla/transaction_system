from django.conf import settings
from django.http import HttpResponseForbidden


class AuthorizationTokenMiddleware:
    """
    Middleware that checks if the Authorization header is present
    and contains a valid token.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return HttpResponseForbidden("Missing Authorization header.")

        try:
            scheme, token = authorization_header.split(' ')
        except ValueError:
            return HttpResponseForbidden("Invalid Authorization header format.")

        if scheme != 'Bearer':
            return HttpResponseForbidden("Invalid authorization scheme.")

        valid_token = getattr(settings, "API_AUTH_TOKEN", None)

        if token != valid_token:
            return HttpResponseForbidden("Invalid token.")
        return self.get_response(request)
