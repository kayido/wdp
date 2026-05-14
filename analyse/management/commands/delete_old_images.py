from django.core.management.base import BaseCommand
from analyse.models import Image
from django.utils import timezone
import datetime
import os

class Command(BaseCommand):
    help = 'Supprime les images vieilles de plus de 7 jours'

    def handle(self, *args, **kwargs):
        limite = timezone.now() - datetime.timedelta(days=7)
        anciennes_images = Image.objects.filter(date_upload__lt=limite)

        compteur = 0
        for image in anciennes_images:
            chemin_image = image.image.path
            if os.path.isfile(chemin_image):
                os.remove(chemin_image)
            image.delete()
            compteur += 1

        self.stdout.write(self.style.SUCCESS(f"{compteur} image(s) supprimée(s)."))

    help = 'Supprime les images uploadées il y a plus de 7 jours'

    def handle(self, *args, **kwargs):
        expiration_date = timezone.now() - datetime.timedelta(days=7)
        old_images = Image.objects.filter(date_upload__lt=expiration_date)

        count = 0
        for img in old_images:
            # Supprimer le fichier image du disque
            if img.image and os.path.isfile(img.image.path):
                os.remove(img.image.path)
            img.delete()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} image(s) supprimée(s)."))

