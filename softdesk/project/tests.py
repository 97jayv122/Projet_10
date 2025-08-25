from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Project, Issue, Comment, Contributor


User = get_user_model()


class BaseAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="alice", password="pass", age=20
        )
        self.user2 = User.objects.create_user(
            username="bob", password="pass", age=30
        )
        self.project = Project.objects.create(
            name="Test Project", description="Description", author=self.user1
        )
        Contributor.objects.create(user=self.user1, project=self.project)
        self.issue = Issue.objects.create(
            project=self.project,
            author=self.user1,
            name="Issue 1",
            description="Issue description",
        )
        self.comment = Comment.objects.create(
            issue=self.issue, author=self.user1, description="Comment 1"
        )
        token_url = reverse("token_obtain_pair")
        response1 = self.client.post(
            token_url, {"username": "alice", "password": "pass"}, format="json"
        )
        response2 = self.client.post(
            token_url, {"username": "bob", "password": "pass"}, format="json"
        )
        self.token1 = response1.data.get("access")
        self.token2 = response2.data.get("access")

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def get_list(self, response):
        data = response.data
        return data.get("results", data)


class ProjectTests(BaseAPITestCase):
    def test_list_projects(self):
        self.authenticate(self.token1)
        url = reverse("project-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        projects = self.get_list(response)
        self.assertTrue(
            any(proj["id"] == self.project.pk for proj in projects)
        )

    def test_retrieve_project(self):
        self.authenticate(self.token1)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.project.pk)

    def test_create_project(self):
        self.authenticate(self.token2)
        url = reverse("project-list")
        data = {"name": "New Project", "description": "New Description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.filter(name="New Project").count(), 1)

    def test_update_project_as_author(self):
        self.authenticate(self.token1)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        data = {"name": "Updated Project", "description": "Updated"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

    def test_update_project_as_non_author(self):
        self.authenticate(self.token2)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        data = {"name": "Fail Update", "description": "Description"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_as_author(self):
        self.authenticate(self.token1)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_delete_project_as_non_author(self):
        self.authenticate(self.token2)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IssueTests(BaseAPITestCase):
    def test_list_issues_as_contributor(self):
        self.authenticate(self.token1)
        url = reverse(
            "project-issues-list", kwargs={"project_pk": self.project.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issues = self.get_list(response)
        self.assertTrue(any(item["id"] == self.issue.pk for item in issues))

    def test_list_issues_as_non_contributor(self):
        self.authenticate(self.token2)
        url = reverse(
            "project-issues-list", kwargs={"project_pk": self.project.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_issue(self):
        self.authenticate(self.token1)
        url = reverse(
            "project-issues-detail",
            kwargs={"project_pk": self.project.pk, "pk": self.issue.pk},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.issue.pk)

    def test_create_issue(self):
        self.authenticate(self.token1)
        url = reverse(
            "project-issues-list", kwargs={"project_pk": self.project.pk}
        )
        data = {"name": "New Issue", "description": "Description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Issue.objects.filter(project=self.project).count(), 2)

    def test_create_issue_non_contributor(self):
        self.authenticate(self.token2)
        url = reverse(
            "project-issues-list", kwargs={"project_pk": self.project.pk}
        )
        data = {"name": "New Issue", "description": "Description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentTests(BaseAPITestCase):
    def test_list_comments_as_contributor(self):
        self.authenticate(self.token1)
        url = reverse(
            "issue-comments-list",
            kwargs={"project_pk": self.project.pk, "issue_pk": self.issue.pk},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comments = self.get_list(response)
        self.assertTrue(
            any(item["id"] == self.comment.pk for item in comments)
        )

    def test_list_comments_as_non_contributor(self):
        self.authenticate(self.token2)
        url = reverse(
            "issue-comments-list",
            kwargs={"project_pk": self.project.pk, "issue_pk": self.issue.pk},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment(self):
        self.authenticate(self.token1)
        url = reverse(
            "issue-comments-list",
            kwargs={"project_pk": self.project.pk, "issue_pk": self.issue.pk},
        )
        data = {"description": "Another comment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(issue=self.issue).count(), 2)

    def test_create_comment_non_contributor(self):
        self.authenticate(self.token2)
        url = reverse(
            "issue-comments-list",
            kwargs={"project_pk": self.project.pk, "issue_pk": self.issue.pk},
        )
        data = {"description": "Another comment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
