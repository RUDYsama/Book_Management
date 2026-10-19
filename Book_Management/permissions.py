from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied


class RoleBasedBookPermission(BasePermission):
    """
    Lab 9.5: Role-Based Access Control (RBAC) for Books API
    
    Permission Matrix:
    ------------------------------------------------------
    Operation            viewer    editor    manager   admin
    ------------------------------------------------------
    GET (Read)             ✓         ✓         ✓         ✓
    POST (Create)          ✗         ✓         ✓         ✓
    PUT/PATCH (Update)     ✗         ✓         ✓         ✓
    DELETE (Delete)        ✗         ✗         ✗         ✓
    ------------------------------------------------------
    """
    message = "Forbidden"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            # Let Authentication / IsAuthenticated handle 401 Unauthorized
            return False

        user_role = getattr(request.user, 'role', 'viewer')

        # Read operations (GET, HEAD, OPTIONS): all authenticated roles can view
        if request.method in SAFE_METHODS:
            if user_role in ['viewer', 'editor', 'manager', 'admin']:
                return True
            raise PermissionDenied("Forbidden")

        # Create & Update operations (POST, PUT, PATCH): editor, manager, admin
        elif request.method in ['POST', 'PUT', 'PATCH']:
            if user_role in ['editor', 'manager', 'admin']:
                return True
            raise PermissionDenied("Forbidden")

        # Delete operations (DELETE): admin only
        elif request.method == 'DELETE':
            if user_role == 'admin':
                return True
            raise PermissionDenied("Forbidden")

        raise PermissionDenied("Forbidden")


def authorize_role(*allowed_roles):
    """
    Factory function matching Handout 9.5 Section 15: authorizeRole(...allowedRoles)
    Returns a DRF BasePermission class for the specified allowed roles.
    """
    class DynamicRolePermission(BasePermission):
        message = "Forbidden"

        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            user_role = getattr(request.user, 'role', 'viewer')
            if user_role in allowed_roles:
                return True
            raise PermissionDenied("Forbidden")

    return DynamicRolePermission


class IsAdminRole(BasePermission):
    message = "Forbidden"

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            getattr(request.user, 'role', '') == 'admin'
        )
