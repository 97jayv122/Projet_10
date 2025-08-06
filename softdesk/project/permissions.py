"""
Permissions for Project, Issue, Comment, and nested routes.

`ProjectPermission` handles both root and nested routes:
- Projects root:
  * GET list & POST create: any authenticated user.
  * GET detail: only project contributors.
  * PATCH/DELETE: only project author.
- Nested under project_pk:
  * GET list & POST create: only project contributors.
  * GET detail: only project contributors.
  * PATCH/DELETE: only author of the nested object.
"""
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import Project

class ProjectPermission(permissions.BasePermission):
    """
    Unified permission for root (projects) and nested routes (issues, comments):
    - Projects root:
      * GET list & POST create: any authenticated user.
      * GET detail: only project contributors.
      * PATCH/DELETE: only project author.
    - Nested under project_pk:
      * GET list & POST create: only project contributors.
      * GET detail: only project contributors.
      * PATCH/DELETE: only author of the nested object.
    """

    def has_permission(self, request, view):
        """
        Global permission check for list and create actions.
        Root list/create: any authenticated user.
        Nested list/create: authenticated contributors only.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False
        project_pk = view.kwargs.get('project_pk')
        if project_pk is None:
            # Root projects route
            return True
        # Nested routes (issues/comments)
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return Project.objects.filter(
                pk=project_pk,
                contributors__user=user
            ).exists()
        return True

    def get_project(self, request, view, obj=None):
        """
        Retrieve Project instance from URL kwargs or object attribute.
        """
        project_pk = view.kwargs.get('project_pk')
        if project_pk:
            return get_object_or_404(Project, pk=project_pk)
        if isinstance(obj, Project):
            return obj
        if hasattr(obj, 'project'):
            return obj.project
        if hasattr(obj, 'issue') and hasattr(obj.issue, 'project'):
            return obj.issue.project
        return None

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for detail, update, and delete:
        - Safe methods: project contributors only.
        - Write methods: only the object author.
        """
        user = request.user
        project = self.get_project(request, view, obj)
        if not user or not user.is_authenticated or project is None:
            return False
        if request.method in permissions.SAFE_METHODS:
            return project.contributors.filter(user=user).exists()
        return hasattr(obj, 'author') and obj.author == user
