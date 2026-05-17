import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from .forms import ClassificationDefineForm
from .models import ClassificationDefine, Image, Signalement


def create_staff_user(username="admin"):
    return User.objects.create_superuser(
        username=username,
        email=f"{username}@example.com",
        password="password",
    )


class SmokePageTests(TestCase):
    def test_public_pages_render_for_anonymous_user(self):
        urls = [
            reverse("home"),
            reverse("upload_image"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_admin_pages_redirect_anonymous_user_to_admin_login(self):
        urls = [
            reverse("galerie"),
            reverse("dashboard"),
            reverse("cartographie"),
            reverse("classification_rule"),
            reverse("signalement"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith("/admin/login/"))

    def test_admin_pages_render_for_staff_user(self):
        self.client.force_login(create_staff_user())
        urls = [
            reverse("galerie"),
            reverse("dashboard"),
            reverse("cartographie"),
            reverse("classification_rule"),
            reverse("signalement"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_staff_without_permission_is_redirected_from_admin_pages(self):
        user = User.objects.create_user(username="limited_staff", password="password", is_staff=True)
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/admin/login/"))

    def test_staff_with_view_image_permission_can_access_dashboard(self):
        user = User.objects.create_user(username="image_viewer", password="password", is_staff=True)
        permission = Permission.objects.get(codename="view_image")
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)


class DashboardApiTests(TestCase):
    def test_dashboard_apis_redirect_anonymous_users(self):
        api_urls = [
            reverse("stats_globales"),
            reverse("gallery_items"),
            reverse("signalements_items"),
            reverse("histogramme"),
            reverse("histogramme_hour"),
        ]

        for url in api_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith("/admin/login/"))

    def test_stats_globales_counts_images_by_annotation(self):
        self.client.force_login(create_staff_user())
        Image.objects.bulk_create(
            [
                Image(image="uploads/full.jpg", nom_fichier="full.jpg", annotation="pleine"),
                Image(image="uploads/empty.jpg", nom_fichier="empty.jpg", annotation="vide"),
                Image(image="uploads/other.jpg", nom_fichier="other.jpg", annotation="pleine"),
            ]
        )

        response = self.client.get(reverse("stats_globales"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total": 3,
                "pleines": 2,
                "videes": 1,
            },
        )

    def test_gallery_items_returns_json_for_authorized_admin(self):
        self.client.force_login(create_staff_user())
        Image.objects.bulk_create(
            [
                Image(image="uploads/full.jpg", nom_fichier="full.jpg", annotation="pleine"),
            ]
        )
        image = Image.objects.get()
        user = User.objects.create_user(username="reporter")
        Signalement.objects.create(
            utilisateur=user,
            image=image,
            adresse="12, Val-de-Marne, France",
            latitude=48.7904,
            longitude=2.4606,
        )

        response = self.client.get(reverse("gallery_items"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["annotation"], "pleine")

    def test_signalements_items_returns_grouped_locations_for_authorized_admin(self):
        self.client.force_login(create_staff_user())
        Image.objects.bulk_create(
            [
                Image(image="uploads/full.jpg", nom_fichier="full.jpg", annotation="pleine"),
            ]
        )
        image = Image.objects.get()
        user = User.objects.create_user(username="reporter")
        Signalement.objects.create(
            utilisateur=user,
            image=image,
            adresse="12, Val-de-Marne, France",
            latitude=48.7904,
            longitude=2.4606,
        )

        response = self.client.get(reverse("signalements_items"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["occur"], 1)


class UploadWorkflowTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_upload_image_with_accented_filename_keeps_workflow_working(self):
        image_bytes = BytesIO()
        PILImage.new("RGB", (32, 32), color=(120, 120, 120)).save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        uploaded_file = SimpleUploadedFile(
            "téléchargement_1.jpg",
            image_bytes.read(),
            content_type="image/jpeg",
        )

        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.post(
                reverse("upload_image"),
                {
                    "image": uploaded_file,
                    "lat": "",
                    "long": "",
                    "adresse": "",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Signalement.objects.count(), 1)
        image = Image.objects.get()
        self.assertIn(image.annotation, ["vide", "pleine"])
        self.assertIsNotNone(image.largeur)
        self.assertIsNotNone(image.hauteur)
        self.assertIsNotNone(image.contraste)

    def test_authenticated_upload_is_linked_to_current_user(self):
        user = User.objects.create_user(username="field_user", password="password")
        self.client.force_login(user)
        image_bytes = BytesIO()
        PILImage.new("RGB", (32, 32), color=(90, 90, 90)).save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        uploaded_file = SimpleUploadedFile(
            "traceability.jpg",
            image_bytes.read(),
            content_type="image/jpeg",
        )

        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.post(
                reverse("upload_image"),
                {
                    "image": uploaded_file,
                    "lat": "",
                    "long": "",
                    "adresse": "",
                    "description": "Signalement de test",
                },
            )

        self.assertEqual(response.status_code, 200)
        signalement = Signalement.objects.get()
        self.assertEqual(signalement.utilisateur, user)
        self.assertEqual(signalement.description, "Signalement de test")

    def test_anonymous_upload_uses_anonymous_reporter_account(self):
        image_bytes = BytesIO()
        PILImage.new("RGB", (32, 32), color=(110, 110, 110)).save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        uploaded_file = SimpleUploadedFile(
            "anonymous.jpg",
            image_bytes.read(),
            content_type="image/jpeg",
        )

        with override_settings(MEDIA_ROOT=self.media_root):
            response = self.client.post(
                reverse("upload_image"),
                {
                    "image": uploaded_file,
                    "lat": "",
                    "long": "",
                    "adresse": "",
                },
            )

        self.assertEqual(response.status_code, 200)
        signalement = Signalement.objects.get()
        self.assertEqual(signalement.utilisateur.username, "anonymous_reporter")
        self.assertFalse(User.objects.filter(username="user2").exists())


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


class ClassificationRuleTests(TestCase):
    def test_classification_define_form_does_not_reference_removed_widget(self):
        form = ClassificationDefineForm()

        self.assertNotIn("area_ratio_rule_2_vide", form.fields)
        self.assertNotIn("area_ratio_rule_2_vide", form.Meta.widgets)

    def test_form_rule_post_creates_rule_and_redirects(self):
        self.client.force_login(create_staff_user())
        data = {
            "num_contours_rule_1_vide": 35,
            "area_ratio_rule_1_vide": 0.25,
            "mean_gray_rule_2_vide": 140,
            "edge_density_rule_2_vide": 0.05,
            "area_ratio_rule_3_vide": 0.1,
            "edge_density_rule_3_vide": 0.02,
            "center_contour_density_rule_4_vide": 0.2,
            "zone_middle_mean_brightness_rule_4_vide": 70,
            "mean_saturation_rule_1_pleine": 75,
            "area_ratio_rule_1_pleine": 0.2,
            "area_ratio_rule_2_pleine": 0.3,
            "num_contours_rule_2_pleine": 60,
            "edge_density_rule_3_pleine": 0.05,
            "mean_saturation_rule_3_pleine": 75,
            "center_contour_density_rule_4_pleine": 0.35,
            "zone_middle_mean_brightness_rule_4_pleine": 80,
            "contrast_rule_5_pleine": 50,
            "entropy_rule_5_pleine": 7.0,
            "is_full_score": 2,
        }

        response = self.client.post(reverse("form_rule"), data=data)

        self.assertRedirects(response, reverse("classification_rule"))
        self.assertEqual(ClassificationDefine.objects.count(), 1)


class AnnotationAccessTests(TestCase):
    def test_anonymous_user_cannot_update_annotation(self):
        Image.objects.bulk_create(
            [
                Image(
                    image="uploads/full.jpg",
                    nom_fichier="full.jpg",
                    annotation="pleine",
                )
            ]
        )
        image = Image.objects.get()

        response = self.client.get(f"/update_annotation/{image.id}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/admin/login/"))
        image.refresh_from_db()
        self.assertEqual(image.annotation, "pleine")


class SignalRegistrationTests(TestCase):
    def test_image_feature_signal_is_registered(self):
        live_receivers = post_save._live_receivers(sender=Image)
        if isinstance(live_receivers, tuple):
            receivers = [receiver for group in live_receivers for receiver in group]
        else:
            receivers = list(live_receivers)

        receiver_names = {getattr(receiver, "__name__", "") for receiver in receivers}

        self.assertIn("extract_image_features", receiver_names)
