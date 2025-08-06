
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Project, Issue, Comment, Contributor
from softdesk.users.models import User


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta: 
        model = Contributor
        fields = ['id', 'user', 'project']
        validators = [
            UniqueTogetherValidator(
                queryset=Contributor.objects.all(),
                fields=['user', 'project'],
                message='Vous êtes déjas contributeur de ce projet'
            )
        ]




class CommentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model  = Comment
        fields = ('id', 'author', 'issue', 'description', 'created_time')
        read_only_fields = ('author', 'issue', 'created_time')


    def validate(self, data):
        # 1) Récupère le view et l'user
        view    = self.context.get('view')
        request = self.context.get('request')
        user    = request.user if request else None

        # 2) Récupère l'issue via issue_pk
        issue_pk = view.kwargs.get('issue_pk') if view else None
        issue = get_object_or_404(Issue, pk=issue_pk)

        # 3) Vérifie que l'utilisateur est contributeur du projet de l'issue
        project = issue.project
        is_contrib = Contributor.objects.filter(
            user=user,
            project=project
        ).exists()
        if not is_contrib:
            raise serializers.ValidationError(
                "Vous ne pouvez pas commenter cette issue."
            )

        # On injecte l'issue dans validated_data pour que perform_create() puisse la consommer
        data['issue'] = issue
        return data



class CommentDetailSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'author', 'created_time', 'description', 'issue']


class IssueSerializer(serializers.ModelSerializer):
    author   = serializers.ReadOnlyField(source='author.username')
    # plus de project = PrimaryKeyRelatedField(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(),  # on remplacera dans __init__
        required=False
    )

    class Meta:
        model  = Issue
        fields = [
            'id', 'author', 'assignee', 'created_time',
            'name', 'tag', 'status', 'priority', 'description',
        ]
        extra_kwargs = {
            'tag':      {'required': False},
            'priority': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # d’abord, essaie le contexte “view” (pour list/create/update via la ViewSet)
        view = self.context.get('view')
        project_pk = None

        if view:
            project_pk = view.kwargs.get('project_pk')
        # sinon, si c’est de la nested-serialization dans ProjectDetailSerializer
        elif hasattr(self, 'parent') and hasattr(self.parent, 'instance'):
            # .parent est un ListSerializer, .parent.parent est ProjectDetailSerializer
            parent = self.parent
            # si on est dans many=True, parent.instance est la liste ; parent.parent.instance est le projet
            if hasattr(parent, 'parent') and hasattr(parent.parent, 'instance'):
                project = parent.parent.instance
                project_pk = getattr(project, 'pk', None)

        # si on a un project_pk, on peut restreindre le queryset des assignees
        if project_pk:
            self.fields['assignee'].queryset = User.objects.filter(
                contribution__project_id=project_pk
            )

    def validate(self, data):
        user = self.context['request'].user
        project_pk = self.context['view'].kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_pk)

        assignee = data.get('assignee')
        # vérifie que l’assigne est bien contributeur
        if assignee and not Contributor.objects.filter(
            user=assignee, project=project
        ).exists():
            raise serializers.ValidationError(
                "L'assigne doit être contributeur du projet."
            )
        # vérifie que l’auteur est contributeur
        if not Contributor.objects.filter(
            user=user, project=project
        ).exists():
            raise serializers.ValidationError(
                "Vous n'êtes pas contributeur de ce projet."
            )
        return data


class IssueDetailSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Issue
        fields = [
            'id',
            'author',
            'assignee',
            'created_time',
            'name',
            'tag',
            'status',
            'priority',
            'description',
            'project',
            'comments',
        ]
    
class ProjectSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Project
        fields = [
            'id',
            'author',
            'created_time',
            'name',
            'type',
            'description',
            ]
        extra_kwargs = {
            'type': {'required': False}
        }


class ProjectDetailSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')
    contributors = ContributorSerializer(many=True, read_only=True)
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'author',
            'created_time',
            'name',
            'type',
            'description',
            'contributors',
            'issues',
            ]