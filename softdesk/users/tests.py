from rest_framework.test import APITestCase
from django.urls import reverse_lazy, reverse
from .models import User


class TestUsers(APITestCase):
    def format_datetime(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class CreateUser(TestUsers):

    def setUp(self):
        self.client.force_authenticate(user=None)
        self.url = reverse_lazy("user-list")

    def test_error_create_user(self):
        before = User.objects.count()
        response = self.client.post(
            self.url,
            {
                "username": "jeanne",
                "password": "tests123",
                "age": 14,
                "can_data_be_shared": True,
                "can_be_contacted": True,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), before)


class GetUser(TestUsers):

    def setUp(self):
        self.user = User.objects.create_user(
            username="marie",
            password="supersecret",
            age=29,
            can_data_be_shared=True,
            can_be_contacted=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_get_user_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["age"], self.user.age)
        self.assertEqual(
            data["can_data_be_shared"], self.user.can_data_be_shared
        )
        self.assertEqual(data["can_be_contacted"], self.user.can_be_contacted)
        self.assertEqual(
            data["created_at"], self.format_datetime(self.user.created_at)
        )


class UpdateUser(TestUsers):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alex",
            password="pass",
            age=30,
            can_data_be_shared=True,
            can_be_contacted=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_patch_user_age(self):
        response = self.client.patch(self.url, {"age": 31}, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 31)
        self.assertTrue(self.user.can_data_be_shared)
        self.assertTrue(self.user.can_be_contacted)

    def test_put_user_full(self):
        new_data = {
            "username": "alexandre",
            "password": "password123",
            "age": 32,
            "can_data_be_shared": True,
            "can_be_contacted": True,
        }
        response = self.client.put(self.url, new_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 32)
        self.assertTrue(self.user.can_data_be_shared)
        self.assertTrue(self.user.can_be_contacted)


class DeleteUser(TestUsers):
    def setUp(self):
        self.user = User.objects.create_user(
            username="camille",
            password="pwd",
            age=28,
            can_data_be_shared=True,
            can_be_contacted=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_soft_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.username.startswith("deleted_"),
            "Le username doit commencer par 'deleted_'",
        )
        self.assertEqual(self.user.email, "", "L'email doit être vidé")
        self.assertFalse(
            self.user.can_be_contacted,
            "can_be_contacted doit être passé à False",
        )
        self.assertFalse(
            self.user.can_data_be_shared,
            "can_data_be_shared doit être passé à False",
        )
        self.assertEqual(self.user.age, 99, "age doit être mis à 99")
        self.assertFalse(
            self.user.has_usable_password(),
            "Le mot de passe doit être rendu inutilisable",
        )
