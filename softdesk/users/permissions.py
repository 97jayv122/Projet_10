"""
Custom permissions for user-related views.
"""
from rest_framework import permissions


class IsSelf(permissions.BasePermission):
    """
    Object-level permission that only allows a user to act on *their own*
    User object.

    Intended usage:
    - Combine with `IsAuthenticated` at the view level.
    - Rely on the view's queryset (e.g., filtering to `request.user`)
      for list views.
    - This class enforces object-level checks for retrieve/update/destroy.
    """

    def has_object_permission(self, request, view, obj):
        """
        Grant access only if the object represents
        the current authenticated user.
        """
        return obj == request.user
