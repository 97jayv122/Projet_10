import uuid
from django.db import models


class Project(models.Model):
    TYPE_CHOICE = [
    ('FRONTEND', 'Front-end'),
    ('BACK_END', 'Back-end'),
    ('IOS', 'iOS'),
    ('ANDROID', 'Android'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICE)
    created_time = models.DateTimeField(auto_now_add=True)


class Issue(models.Model):
    TAG_CHOICES = [('BUG','Bug'),('FEATURE','Feature'),('TASK','Task')]
    PRIORITY_CHOICES = [('LOW','Low'),('MEDIUM','Medium'),('HIGH','High')]
    STATUS_CHOICES = [('TODO','To Do'),('IN_PROGRESS','In Progress'),('FINISHED','Finished')]

    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='issues')
    name = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='TODO')
    created_time = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(blank=False)
    issue = models.ForeignKey('project.Issue', on_delete=models.CASCADE, related_name='comments')
    created_time =  models.DateTimeField(auto_now_add=True)
