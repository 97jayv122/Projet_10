
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

    # issue = serializers.HyperlinkedRelatedField(
    #     many=False,
    #     read_only=True,
    #     view_name='issue-detail'
    # )
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'created_time',
            'description',
            'issue',
        ]


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    # assignee = serializers.PrimaryKeyRelatedField(
    #     queryset=Contributor.objects.none(),
    #     allow_null=True, required=False
    # )
    

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
        ]

    
    # def get_valid_assignees_queryset(self):
    #     project_id = self.initial_data.get('project')
    #     return User.objects.filter(contribution__project_id=project_id)

    def validate(self, data):
        assignee = data.get('assignee')
        if assignee and not Contributor.objects.filter(user=assignee, project_id=data['project'].id).exists():
            raise serializers.ValidationError("L'assigne doit être contributeur du projet.")
        return data
    
class ProjectSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')
    contributor = ContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'author',
            'created_time',
            'name',
            'type',
            'description',
            'contributor',
            ]


class ProjectDetailSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Project
        fields = [
            'id',
            'author'
            'created_time',
            'name',
            'description',
            'code',
            ]