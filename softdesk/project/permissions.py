"""
Permissions for Project, Issue, Comment, and nested routes.

Behavior:
- Root /projects:
  * GET list & POST create: any authenticated user.
  * GET detail: only contributors.
  * PATCH/DELETE: only project author.
- Nested under project_pk (issues, comments):
  * 404 if the project (or issue) does not exist.
  * GET list & POST create: only project contributors.
  * GET detail: only project contributors.
  * PATCH/DELETE: only author of the nested object.
"""
from rest_framework import permissions
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from .models import Project, Issue  # <-- import Issue for nested existence checks


class ProjectPermission(permissions.BasePermission):
    """
    Unified permission for root and nested routes with proper 404 vs 403 semantics.
    """

    def has_permission(self, request, view):
        """
        Global permission check (called for list/create views).
        - Root list/create: allow any authenticated user.
        - Nested list/create: first ensure the resource exists (404), then
          require contributor (403 if not).
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        project_pk = view.kwargs.get("project_pk")

        # Root /api/projects/ (no project_pk in URL)
        if project_pk is None:
            return True  # authenticated users may list/create projects

        # --- Nested under a project ---
        # 1) Existence checks -> raise 404 if missing
        if not Project.objects.filter(pk=project_pk).exists():
            raise NotFound("Project not found.")

        issue_pk = view.kwargs.get("issue_pk")
        if issue_pk is not None:
            if not Issue.objects.filter(pk=issue_pk, project_id=project_pk).exists():
                raise NotFound("Issue not found.")

        # 2) Role checks -> 403 if not contributor for read/list/create
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return Project.objects.filter(
                pk=project_pk, contributors__user=user
            ).exists()

        # Updates/deletes are validated at object level (author check)
        return True

    def get_project(self, request, view, obj=None):
        """
        Retrieve the Project instance from URL kwargs or the object graph.
        Uses 404 on missing project when project_pk is present.
        """
        project_pk = view.kwargs.get("project_pk")
        if project_pk:
            return get_object_or_404(Project, pk=project_pk)
        if isinstance(obj, Project):
            return obj
        if hasattr(obj, "project"):
            return obj.project
        if hasattr(obj, "issue") and hasattr(obj.issue, "project"):
            return obj.issue.project
        return None

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for detail/update/delete:
        - SAFE methods: allowed to project contributors.
        - Write methods: only the object's author.
        """
        user = request.user
        project = self.get_project(request, view, obj)
        if not user or not user.is_authenticated or project is None:
            return False

        if request.method in permissions.SAFE_METHODS:
            return project.contributors.filter(user=user).exists()

        return hasattr(obj, "author") and obj.author == user
