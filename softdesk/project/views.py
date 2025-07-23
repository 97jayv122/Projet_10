from django.shortcuts import render
from rest_framework import permissions, viewsets
from .models import Project, Issue, Comment, Contributor
from .permissions import IsContributorOrAuthor, IsAuthorOrReadOnly
from .serializers import (
    ProjectSerializer,
    # ProjectDetailSerializer,
    IssueSerializer,
    # IssueDetailSerializer,
    CommentSerializer,
    # CommentDetailSerializer
    ContributorSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project to be viewed or edited
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAuthorOrReadOnly,
        ]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)




class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issue to be viewed or edited
    """

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributorOrAuthor
        ]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsContributorOrAuthor
        ]

    def get_queryset(self):
        queryset = Comment.objects.all()
        owner = self.request.user
        queryset = queryset.filter(author=owner)
        return queryset


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        