from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that maps token claims to Book_Management.models.User
    """
    def get_user(self, validated_token):
        user_id = validated_token.get('id') or validated_token.get('user_id') or validated_token.get(api_settings.USER_ID_CLAIM)
        if not user_id:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        return user
