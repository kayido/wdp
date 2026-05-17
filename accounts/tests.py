from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


def create_staff_user(username="admin"):
    return User.objects.create_superuser(
        username=username,
        email=f"{username}@example.com",
        password="password",
    )


class AuthWorkflowTests(TestCase):
    def test_register_redirects_to_admin_login(self):
        response = self.client.get(reverse("register"))

        self.assertRedirects(response, reverse("login"))

    def test_login_rejects_non_staff_user(self):
        User.objects.create_user(username="existing_user", password="StrongPass123!")

        response = self.client.post(
            reverse("login"),
            {
                "username": "existing_user",
                "password": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "Accès réservé aux administrateurs.")

    def test_login_authenticates_staff_user(self):
        user = create_staff_user(username="existing_admin")

        response = self.client.post(
            reverse("login"),
            {
                "username": user.username,
                "password": "password",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

# Create your tests here.
