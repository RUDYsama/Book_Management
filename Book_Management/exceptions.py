from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


def custom_exception_handler(exc, context):
    """
    Custom exception handler to match Lab 9.4 & Lab 9.5 exact status codes and response messages:
    - Missing Token -> HTTP 401: {"message": "Access token required"}
    - Invalid or Expired Token -> HTTP 403: {"message": "Invalid or expired token"}
    - Role Forbidden (RBAC) -> HTTP 403: {"message": "Forbidden"}
    """
    response = exception_handler(exc, context)

    if response is not None:
        # 1. Invalid or expired token (SimpleJWT InvalidToken or AuthenticationFailed)
        if isinstance(exc, (InvalidToken, AuthenticationFailed)) or 'token_not_valid' in str(response.data):
            return Response(
                {"message": "Invalid or expired token"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Missing token (NotAuthenticated) -> HTTP 401
        if isinstance(exc, NotAuthenticated) or response.status_code == status.HTTP_401_UNAUTHORIZED:
            return Response(
                {"message": "Access token required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 3. Role-Based Access Control / Authorization failure -> HTTP 403 Forbidden
        if isinstance(exc, (PermissionDenied, DjangoPermissionDenied)) or response.status_code == status.HTTP_403_FORBIDDEN:
            return Response(
                {"message": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN
            )

    return response
