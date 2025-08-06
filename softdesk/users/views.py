import uuid
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsSelf

class UserViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def perform_destroy(self, instance):

        instance.username = f"deleted_{uuid.uuid4().hex}"
        instance.email = ""
        instance.set_unusable_password()
        instance.can_be_contacted = False
        instance.can_data_be_shared = False
        instance.age = 99
        instance.save()
