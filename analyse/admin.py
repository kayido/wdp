from django.contrib import admin
from .models import (
    Image, Signalement, ZoneRisques, ClassificationDefine
)

admin.site.register(Image)
admin.site.register(Signalement)
admin.site.register(ZoneRisques)
admin.site.register(ClassificationDefine)