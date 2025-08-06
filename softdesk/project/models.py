"""
Data models for Projects, Issues, Comments, and Contributors.

- Project: represents a work project with name, description, type,
  creation timestamp, and author relationship.
- Issue: task or bug within a project, with priority, tag, status,
  timestamps, author, and optional assignee.
- Contributor: links a User to a Project, ensuring uniqueness per pair.
- Comment: feedback or discussion entry on an Issue, with UUID primary key,
  description, timestamp, and author.
"""
import uuid
from django.db import models
from softdesk.users.models import User


class Project(models.Model):
    """
    A project entity that groups issues and contributors.

    Attributes:
    - name: the project title.
    - description: detailed information about the project.
    - type: category of the project (Frontend, Back-end, iOS, Android).
    - created_time: timestamp when the project was created.
    - author: the User who created the project.
    """
    TYPE_CHOICE = [
    ('FRONTEND', 'Front-end'),
    ('BACK_END', 'Back-end'),
    ('IOS', 'iOS'),
    ('ANDROID', 'Android'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICE)
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
        )

    def __str__(self):
        """String representation of the Project."""
        return self.name

class Issue(models.Model):
    """
    Represents a task, feature, or bug within a project.

    Attributes:
    - project: foreign key to the parent Project.
    - name: brief title of the issue.
    - description: detailed description.
    - priority: priority level (Low, Medium, High).
    - tag: type classification (Bug, Feature, Task).
    - status: workflow status (To Do, In Progress, Finished).
    - created_time: timestamp when the issue was created.
    - author: creator of the issue.
    - assignee: optional User assigned to resolve the issue.
    """
    TAG_CHOICES = [('BUG','Bug'),('FEATURE','Feature'),('TASK','Task')]
    PRIORITY_CHOICES = [
        ('LOW','Low'),
        ('MEDIUM','Medium'),
        ('HIGH','High')
        ]
    STATUS_CHOICES = [
        ('TODO','To Do'),
        ('IN_PROGRESS','In Progress'),
        ('FINISHED','Finished')
        ]

    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='issues')
    name = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='TODO'
        )
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_issue'
        )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_issues'
        )

    def __str__(self):
        """String representation of the Issue."""
        return self.name
    

class Contributor(models.Model):
    """
    Links a User to a Project as a contributor.

    Enforces a unique (user, project) pairing.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contribution'
        )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributors'
        )

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        """String representation of the Contributor."""
        return f'{self.user.username} -> {self.project.name}'


class Comment(models.Model):
    """
    A comment on an Issue, authored by a User.

    Attributes:
    - id: UUID primary key for unique identification.
    - description: text content of the comment.
    - issue: foreign key to the related Issue.
    - created_time: timestamp when the comment was created.
    - author: the User who authored the comment.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
        )
    description = models.TextField(blank=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    created_time =  models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_comment'
        )

    def __str__(self):
        """String representation of the Comment."""
        return f'Comment by {self.author.username} on {self.issue.name}'