"""
Serializers for Project, Issue, Comment, and Contributor APIs with English docstrings.

- ContributorSerializer: manages user-project relationships
    with hidden current user and uniqueness constraint.
- CommentSerializer: enforces contributor-only commenting and injects issue context.
- CommentDetailSerializer: hyperlink-based detailed view for comments.
- IssueSerializer: filters assignee options to project contributors and validates roles.
- IssueDetailSerializer: includes nested comments for issues.
- ProjectSerializer: basic project fields with read-only author.
- ProjectDetailSerializer: nested contributors and issues within project detail.
"""
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Project, Issue, Comment, Contributor
from softdesk.users.models import User

class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for Contributor model.

    - Hides the user field by defaulting to the current authenticated user.
    - Ensures a user cannot be added twice to the same project.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']
        validators = [
            UniqueTogetherValidator(
                queryset=Contributor.objects.all(),
                fields=['user', 'project'],
                message='You are already a contributor to this project.'
            )
        ]

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.

    - Read-only 'id' and 'author' fields.
    - Validates that only project contributors can create comments.
    - Injects the parent Issue instance into validated data.
    """
    id = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ('id',
                  'author',
                  'issue',
                  'description',
                  'created_time'
                  )
        read_only_fields = ('author', 'issue', 'created_time')

    def validate(self, data):
        """
        Ensure the request user is a contributor 
        to the issue's project before commenting.
        """
        view = self.context.get('view')
        request = self.context.get('request')
        user = request.user if request else None

        issue_pk = view.kwargs.get('issue_pk') if view else None
        issue = get_object_or_404(Issue, pk=issue_pk)

        if not Contributor.objects.filter(
            user=user,
            project=issue.project
            ).exists():
            raise serializers.ValidationError(
                "You cannot comment on this issue."
                )

        data['issue'] = issue
        return data

class CommentDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Detailed serializer for Comment with a hyperlink to the issue.
    """
    class Meta:
        model = Comment
        fields = ['id',
                  'author',
                  'created_time',
                  'description',
                  'issue'
                  ]

class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.

    - Read-only 'author' field.
    - 'assignee' field limited to contributors of the project.
    - Validates that both author and assignee are project contributors.
    """
    author = serializers.ReadOnlyField(source='author.username')
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(),
        required=False
    )

    class Meta:
        model = Issue
        fields = ['id',
                  'author',
                  'assignee',
                  'created_time',
                  'name', 'tag',
                  'status',
                  'priority',
                  'description'
                  ]
        extra_kwargs = {
            'tag': {'required': False},
            'priority': {'required': False}
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view = self.context.get('view')
        project_pk = None

        if view:
            project_pk = view.kwargs.get('project_pk')
        elif hasattr(self, 'parent') and hasattr(self.parent, 'instance'):
            parent = self.parent
            if hasattr(parent, 'parent') and hasattr(parent.parent, 'instance'):
                project_pk = getattr(parent.parent.instance, 'pk', None)

        if project_pk:
            self.fields['assignee'].queryset = User.objects.filter(
                contribution__project_id=project_pk
                )

    def validate(self, data):
        """
        Validate that the author and optional 
        assignee are contributors to the project.
        """
        user = self.context['request'].user
        project_pk = self.context['view'].kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_pk)

        assignee = data.get('assignee')
        if assignee and not Contributor.objects.filter(
            user=assignee,
            project=project
            ).exists():
            raise serializers.ValidationError(
                "Assignee must be a project contributor."
                )
        if not Contributor.objects.filter(
            user=user,
            project=project
            ).exists():
            raise serializers.ValidationError(
                "You are not a contributor to this project."
                )
        return data

class IssueDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Issue including nested comments.
    """
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = ['id',
                  'author',
                  'assignee',
                  'created_time',
                  'name',
                  'tag',
                  'status',
                  'priority',
                  'description',
                  'project',
                  'comments'
                  ]

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model with read-only author.
    """
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Project
        fields = ['id',
                  'author',
                  'created_time',
                  'name', 'type',
                  'description'
                  ]
        extra_kwargs = {'type': {'required': False}}

class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Project including contributors and issues.
    """
    author = serializers.ReadOnlyField(source='author.username')
    contributors = ContributorSerializer(many=True, read_only=True)
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id',
                  'author',
                  'created_time',
                  'name',
                  'type',
                  'description',
                  'contributors',
                  'issues'
                  ]
