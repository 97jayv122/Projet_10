from django.shortcuts import render
from rest_framework import permissions, viewsets
from .models import Project, Issue, Comment, Contributor
from .permissions import IsContributorOrAuthor, IsAuthorOrReadOnly
from .serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    # CommentDetailSerializer
    ContributorSerializer
)

class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()



class ProjectViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows project to be viewed or edited
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAuthorOrReadOnly,   
        ]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)


class IssueViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows issue to be viewed or edited
    """

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributorOrAuthor
        ]
    def get_queryset(self): 
        user = self.request.user
        return Issue.objects.filter(project__contributor__user=user)


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributorOrAuthor
        ]
    
    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(issue__project__contributor__user=user)

    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        