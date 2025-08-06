"""
REST API Views for Projects, Issues, Comments, and Contributor management.

Endpoints:
- Projects: list, create (auto-add contributor), retrieve,
  update/delete (author-only).
- Issues & Comments: nested under projects; list/create (contributors only),
  retrieve, update/delete (author-only).
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
    """
    Override default serializer for retrieve actions.

    If `detail_serializer_class` is provided and action is `retrieve`,
    return it instead of the default serializer_class.
    """
    detail_serializer_class = None

    def get_serializer_class(self):
        """
        Return the serializer class for the current action.

        - For `retrieve`: return `detail_serializer_class` if set.
        - Otherwise: fall back to the default.
        """
        if self.action == 'retrieve' and self.detail_serializer_class:
            return self.detail_serializer_class
        return super().get_serializer_class()

class ProjectViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    ViewSet for Project model.

    Actions:
    - list (GET): all projects (authenticated users only).
    - create (POST): new project; current user becomes author and contributor.
    - retrieve (GET): project details (contributors only).
    - update (PATCH)/destroy (DELETE): project author only.
    """
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        """
        Return base queryset for projects.

        Permissions handle access control for detail views.
        """
        return Project.objects.all()

    def perform_create(self, serializer):
        """
        Create a new Project and add the author as Contributor.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.get_or_create(
            user=self.request.user,
            project=project
            )

class IssueViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    """
    ViewSet for Issue model nested under Project.

    Actions:
    - list (GET): issues of a specific project (contributors only).
    - create (POST): new issue; current user becomes author.
    - retrieve (GET): issue details (contributors only).
    - update (PATCH)/destroy (DELETE): issue author only.
    """
    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        """
        Return issues filtered by the parent project.
        """
        project_pk = self.kwargs['project_pk']
        return Issue.objects.filter(project_id=project_pk)

    def perform_create(self, serializer):
        """
        Create a new Issue linked to the specified project.
        """
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(author=self.request.user, project=project)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model nested under Issue and Project.

    Actions:
    - list (GET): comments of a specific issue (contributors only).
    - create (POST): new comment; current user becomes author.
    - retrieve (GET): comment details (contributors only).
    - update (PATCH)/destroy (DELETE): comment author only.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        """
        Return comments filtered by the parent project and issue.
        """
        project_pk = self.kwargs['project_pk']
        issue_pk = self.kwargs['issue_pk']
        return Comment.objects.filter(
            issue__project_id=project_pk,
            issue_id=issue_pk
        )

    def perform_create(self, serializer):
        """
        Create a new Comment linked to the specified issue.
        """
        issue = get_object_or_404(
            Issue.objects.filter(project_id=self.kwargs['project_pk']),
            pk=self.kwargs['issue_pk']
        )
        serializer.save(author=self.request.user, issue=issue)

class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contributor model.

    Actions:
    - list (GET): list contributions for current user.
    - create (POST): add current user as contributor to a project.
    - update/destroy: not used (contributors cannot be modified directly).
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return contributions only for the current user.
        """
        return Contributor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new Contributor linking current user to a project.
        """
        serializer.save(user=self.request.user)
