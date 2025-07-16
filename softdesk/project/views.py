from django.shortcuts import render
from rest_framework import permissions, viewsets
from .models import Project, Issue, Comment
from .serializers import (
    ProjectSerializer,
    IssueSerializer,
    CommentSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project to be viewed or edited
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issue to be viewed or edited
    """

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comment to be viewed or edited
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer