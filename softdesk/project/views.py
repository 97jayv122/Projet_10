"""
REST API Views for Projects, Issues, Comments, and Contributor management.

- Projects: list, create (auto-add contributor), retrieve, update/delete (author-only).
- Issues & Comments: nested under projects; list/create (contributors only), retrieve, update/delete (author-only).
"""
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from .models import Project, Issue, Comment, Contributor
from .permissions import ProjectPermission
from .serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    ContributorSerializer,
)

class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class:
            return self.detail_serializer_class
        return super().get_serializer_class()

class ProjectViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.all()

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.get_or_create(user=self.request.user, project=project)

class IssueViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        return Issue.objects.filter(project_id=project_pk)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(author=self.request.user, project=project)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        issue_pk = self.kwargs['issue_pk']
        return Comment.objects.filter(issue__project_id=project_pk, issue_id=issue_pk)

    def perform_create(self, serializer):
        issue = get_object_or_404(
            Issue.objects.filter(project_id=self.kwargs['project_pk']),
            pk=self.kwargs['issue_pk']
        )
        serializer.save(author=self.request.user, issue=issue)

class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
