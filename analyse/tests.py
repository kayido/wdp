import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from .forms import ClassificationDefineForm
from .models import ClassificationDefine, Image, Signalement


class SmokePageTests(TestCase):
    def test_main_pages_render(self):
        urls = [
            reverse("home"),
            reverse("upload_image"),
            reverse("galerie"),
            reverse("dashboard"),
            reverse("cartographie"),
            reverse("classification_rule"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)


class DashboardApiTests(TestCase):
    def test_stats_globales_counts_images_by_annotation(self):
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


class ClassificationRuleTests(TestCase):
    def test_classification_define_form_does_not_reference_removed_widget(self):
        form = ClassificationDefineForm()

        self.assertNotIn("area_ratio_rule_2_vide", form.fields)
        self.assertNotIn("area_ratio_rule_2_vide", form.Meta.widgets)

    def test_form_rule_post_creates_rule_and_redirects(self):
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


class SignalRegistrationTests(TestCase):
    def test_image_feature_signal_is_registered(self):
        live_receivers = post_save._live_receivers(sender=Image)
        if isinstance(live_receivers, tuple):
            receivers = [receiver for group in live_receivers for receiver in group]
        else:
            receivers = list(live_receivers)

        receiver_names = {getattr(receiver, "__name__", "") for receiver in receivers}

        self.assertIn("extract_image_features", receiver_names)
