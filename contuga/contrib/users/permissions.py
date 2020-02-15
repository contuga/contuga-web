from rest_framework import permissions


class IsHimself(permissions.BasePermission):
    """
    Allow users to access only their own objects
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsNotAuthenticated(permissions.BasePermission):
    """
    Allows access only to unauthenticated users.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated
