from rest_framework import permissions


class IsContributorOrAuthor(permissions.BasePermission):
     
    def has_object_permission(self, request, view, obj):
        user = request.user
        project = getattr(obj, 'project', None)
        if not project:
            return False
        is_contributor = project.contributors.filter(user=user).exists()
        if request.method in permissions.SAFE_METHODS:
            return is_contributor
        is_author = hasattr(obj, 'author') and obj.author == user
        return is_contributor and is_author


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if obj.author == user:
            return True
        return False