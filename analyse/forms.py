from django import forms
from .models import Image
 
class UploadForm(forms.ModelForm):
    class Meta:
        model = Image
        #fields = ['image', 'annotation']
        fields = ['image']

        # widgets = {
        #     'annotation': forms.Select(attrs={'class': 'form-control'}),
        # }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['annotation'].choices = [
        #     ('vide', 'Vide'),
        #     ('pleine', 'Pleine')
        # ]
 
 

from .models import ZoneRisques

class ZoneRisquesForm(forms.ModelForm):
    class Meta:
        model = ZoneRisques
        fields = ['libelle', 'adresse', 'longitude', 'latitude', 'date_debut_validite', 'date_fin_validite', 'niveau']



from django import forms
from .models import ClassificationDefine

class ClassificationDefineForm(forms.ModelForm):
    class Meta:
        model = ClassificationDefine
        fields = '__all__'  # Tu peux aussi lister les champs manuellement si tu préfères un certain ordre

        widgets = {
            'num_contours_rule_1_vide': forms.NumberInput(attrs={'class': 'form-control'}),
            'mean_gray_rule_2_vide': forms.NumberInput(attrs={'class': 'form-control'}),
            'edge_density_rule_2_vide': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'area_ratio_rule_3_vide': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'edge_density_rule_3_vide': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'center_contour_density_rule_4_vide': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'zone_middle_mean_brightness_rule_4_vide': forms.NumberInput(attrs={'class': 'form-control'}),
            'mean_saturation_rule_1_pleine': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_ratio_rule_1_pleine': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'area_ratio_rule_2_pleine': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'num_contours_rule_2_pleine': forms.NumberInput(attrs={'class': 'form-control'}),
            'edge_density_rule_3_pleine': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'mean_saturation_rule_3_pleine': forms.NumberInput(attrs={'class': 'form-control'}),
            'center_contour_density_rule_4_pleine': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'zone_middle_mean_brightness_rule_4_pleine': forms.NumberInput(attrs={'class': 'form-control'}),
            'contrast_rule_5_pleine': forms.NumberInput(attrs={'class': 'form-control'}),
            'entropy_rule_5_pleine': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'is_full_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }
