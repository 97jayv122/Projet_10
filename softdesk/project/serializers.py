
from rest_framework import serializers

from .models import Project, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'code',
            'created_time',
            'issues'
            ]
        

class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = [
            'id',
            'name',
            'tag',
            'status',
            'priority',
            'description',
            'project',
        ]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'id',
            'name',
            'description',
            'issue'
        ]