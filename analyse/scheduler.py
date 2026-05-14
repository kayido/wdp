# analyse/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from analyse.models import Image
from django.utils import timezone
from datetime import timedelta

def delete_old_images():
    expiration = timezone.now() - timedelta(days=7)
    anciennes_images = Image.objects.filter(date_upload__lt=expiration)
    count = anciennes_images.count()
    anciennes_images.delete()
    print(f"{count} image(s) supprimée(s).")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_images, 'interval', weeks=1)
    scheduler.start()
