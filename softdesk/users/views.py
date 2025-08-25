"""
User viewset for managing user accounts.
"""
import uuid
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsSelf


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet exposing user endpoints for registration and self-service profile
    operations (retrieve/update/delete).

    - POST /users/ (create): open to unauthenticated users (registration).
    - GET /users/ (list): returns only the current user's record.
    - GET /users/{id}/ (retrieve): current user only.
    - PATCH/PUT /users/{id}/ (update/partial_update): current user only.
    - DELETE /users/{id}/ (destroy): soft-delete/anonymize current user.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Return per-action permissions.

        - create: AllowAny (public registration).
        - others: user must be authenticated AND operate on their own record
          (IsSelf).
        """
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        """
        Limit list/retrieve queries to the current user.

        This prevents user enumeration and ensures that even if a different
        primary key is requested, the filtered queryset will not expose other
        users.
        """
        return User.objects.filter(pk=self.request.user.pk)

    def perform_destroy(self, instance):
        """
        Soft-delete/anonymize the user instead of removing the row.

        Scrambles the username, clears the email, invalidates the password,
        and resets consent/age flags.
        """
        instance.username = f"deleted_{uuid.uuid4().hex}"
        instance.email = ""
        instance.set_unusable_password()
        instance.can_be_contacted = False
        instance.can_data_be_shared = False
        instance.age = 99
        instance.save()
