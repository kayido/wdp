# analyse/signals.py
import os
from PIL import Image as PILImage
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Image as UploadedImage
import cv2
import numpy as np

@receiver(post_save, sender=UploadedImage)
def extract_image_features(sender, instance, created, **kwargs):
    if not created or not instance.image:
        return

    path = instance.image.path
    taille_ko = round(os.path.getsize(path) / 1024)

    # PIL pour les tailles et moyennes RVB
    img_pil = PILImage.open(path).convert("RGB")
    largeur, hauteur = img_pil.size
    pixels = list(img_pil.getdata())
    total_pixels = len(pixels)
    r_moyen = round(sum(p[0] for p in pixels) / total_pixels)
    v_moyen = round(sum(p[1] for p in pixels) / total_pixels)
    b_moyen = round(sum(p[2] for p in pixels) / total_pixels)

    # Conversion OpenCV
    img_cv = cv2.imread(path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Luminance moyenne
    luminance_moyenne = float(np.mean(gray))

    # Contraste = max - min
    contraste = float(np.max(gray) - np.min(gray))

    # Détection de contours avec Canny
    contours = cv2.Canny(gray, threshold1=100, threshold2=200)
    has_contours = np.any(contours)

    # Mise à jour de l'objet
    instance.largeur = largeur
    instance.hauteur = hauteur
    instance.taille_ko = taille_ko
    instance.r_moyen = r_moyen
    instance.v_moyen = v_moyen
    instance.b_moyen = b_moyen
    instance.luminance_moyenne = luminance_moyenne
    instance.contraste = contraste
    instance.has_contours = has_contours
    instance.save()
