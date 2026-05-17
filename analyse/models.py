from django.db import models
from django.contrib.auth.models import User

### IMAGE / MÉTADONNÉES ###
class Image(models.Model):
    image = models.ImageField(upload_to='uploads/')
    nom_fichier = models.CharField(max_length=255)
    annotation = models.CharField(
        max_length=20,
        choices=[
            ('vide', 'Vide'),
            ('moitie', 'À moitié pleine'),
            ('pleine', 'Pleine'),
            ('debordante', 'Débordante'),
            ('depot_sauvage', 'Dépôt sauvage')
        ],
        blank=True,
        null=True
    )
    date_upload = models.DateTimeField(auto_now_add=True)
    largeur = models.IntegerField(null=True, blank=True)
    hauteur = models.IntegerField(null=True, blank=True)
    taille_ko = models.IntegerField(null=True, blank=True)
    r_moyen = models.IntegerField(null=True, blank=True)
    v_moyen = models.IntegerField(null=True, blank=True)
    b_moyen = models.IntegerField(null=True, blank=True)
#    
    luminance_moyenne = models.FloatField(null=True, blank=True)
    has_contours = models.BooleanField(null=True, blank=True)
    # Pour le contraste
    contraste = models.FloatField(null=True, blank=True)

# Pour l’histogramme compressé (optionnel : chaîne JSON ou texte)
    histogramme = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom_fichier



class ZoneRisques(models.Model):
    libelle = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    longitude = models.FloatField()  # Corrigé la précision
    latitude = models.FloatField()
    date_debut_validite = models.DateField(null=True, blank=True)
    date_fin_validite = models.DateField(null=True, blank=True)
    niveau = models.CharField(max_length=50)

    def __str__(self):
        return self.libelle

### SIGNALEMENT ###
class Signalement(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='signalements')
    description = models.TextField(blank=True)
    adresse = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    date_signalement = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey(ZoneRisques, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Signalement de {self.utilisateur.username} le {self.date_signalement}"
    





class ClassificationDefine(models.Model):
    # Règle 1 Vide
    num_contours_rule_1_vide = models.IntegerField(default=35)
    area_ratio_rule_1_vide = models.FloatField(default=0.25)

    # Règle 2 Vide
    mean_gray_rule_2_vide = models.IntegerField(default=140)
    edge_density_rule_2_vide = models.FloatField(default=0.05)

    # Règle 3 Vide
    area_ratio_rule_3_vide = models.FloatField(default=0.1)
    edge_density_rule_3_vide = models.FloatField(default=0.02)

    # Règle 4 Vide
    center_contour_density_rule_4_vide = models.FloatField(default=0.2)
    zone_middle_mean_brightness_rule_4_vide = models.IntegerField(default=70)

    # Règle 1 Pleine
    mean_saturation_rule_1_pleine = models.IntegerField(default=75)
    area_ratio_rule_1_pleine = models.FloatField(default=0.2)

    # Règle 2 Pleine
    area_ratio_rule_2_pleine = models.FloatField(default=0.3)
    num_contours_rule_2_pleine = models.IntegerField(default=60)

    # Règle 3 Pleine
    edge_density_rule_3_pleine = models.FloatField(default=0.05)
    mean_saturation_rule_3_pleine = models.IntegerField(default=75)

    # Règle 4 Pleine
    center_contour_density_rule_4_pleine = models.FloatField(default=0.35)
    zone_middle_mean_brightness_rule_4_pleine = models.IntegerField(default=80)

    # Règle 5 Pleine
    contrast_rule_5_pleine = models.IntegerField(default=50)
    entropy_rule_5_pleine = models.FloatField(default=7.0)

    # Score
    is_full_score = models.IntegerField(default=2)

    active = models.BooleanField(default=False)

    
    def __str__(self):
        return f"ImageAnalysis #{self.id} - Full Score: {self.is_full_score}"



