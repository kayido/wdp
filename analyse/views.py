from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from analyse.règles_classification import classification_par_regles
from .forms import UploadForm, ClassificationDefineForm
from .models import Image, Signalement, User
from PIL import Image as PILImage
import numpy as np
import os
import cv2
import json
import io
import matplotlib.pyplot as plt
from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour
from .utils import haversine
from .utils import transforms_adresse, contient_adresse
from django.db.models import Count
from django.http import JsonResponse
from .models import Image
from django.db.models.functions import ExtractWeekDay
from django.db.models import Count
from io import BytesIO
from django.core.files.base import ContentFile
from .ML import extract_features, classify_trash_can

# Page d'accueil avec upload + extraction automatique
def home(request):
    message = ""
    form = UploadForm()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_obj = form.save(commit=False)
            image_obj.nom_fichier = os.path.basename(image_obj.image.name)
            image_obj.save()

            original_path = image_obj.image.path
            original_name = os.path.splitext(os.path.basename(image_obj.image.name))[0]

            with PILImage.open(original_path) as img:
                if img.format != "WEBP":
                    img = img.convert("RGBA")  # Pour gérer la transparence si existante
                    webp_io = BytesIO()
                    img.save(webp_io, format="WEBP", lossless=True)

                    webp_filename = f"{original_name}.webp"
                    # Remplace le fichier original par la version WebP lossless
                    image_obj.image.save(webp_filename, ContentFile(webp_io.getvalue()), save=False)

            path = image_obj.image.path

            pil_img = PILImage.open(path).convert("RGB")
            image_obj.largeur, image_obj.hauteur = pil_img.size
            image_obj.taille_ko = round(os.path.getsize(path) / 1024)

            img_array = np.array(pil_img.resize((100, 100)))
            
            if len(img_array.shape) == 3:
                image_obj.r_moyen = int(np.mean(img_array[:, :, 0]))
                image_obj.v_moyen = int(np.mean(img_array[:, :, 1]))
                image_obj.b_moyen = int(np.mean(img_array[:, :, 2]))
            else:
                v = int(np.mean(img_array))
                image_obj.r_moyen = image_obj.v_moyen = image_obj.b_moyen = v
            # Luminance moyenne
            luminance = 0.2126 * img_array[:, :, 0] + 0.7152 * img_array[:, :, 1] + 0.0722 * img_array[:, :, 2]
            image_obj.luminance_moyenne = float(np.mean(luminance))
            # Contraste (OpenCV)
            cv_img = cv2.imread(path)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            image_obj.contraste = float(np.max(gray) - np.min(gray))
            # Histogramme compressé
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_list = hist.flatten().tolist()
            image_obj.histogramme = json.dumps(hist_list[:64])  # 64 premières valeurs
            
            
            message = "Image envoyée et analysée avec succès !"

            features = extract_features(image_path=path, debug=None, filename=image_obj.nom_fichier)
            image_obj.annotation = classify_trash_can(features)
            print(image_obj.annotation)
            
            image_obj.save()

            signalement = Signalement()
            signalement.description = ""
            if request.POST.get("lat") =="" or request.POST.get("long") =="":
                signalement.latitude = 48.7904 
                signalement.longitude = 2.4606
                signalement.adresse = "12,Val-de-Marne, France métropolitaine, 94, France"

            else :
                signalement.latitude = request.POST.get("lat")
                signalement.longitude = request.POST.get("long")
                signalement.adresse = request.POST.get("adresse")
            
            
            signalement.image = image_obj


            zones = ZoneRisques.objects.all()
            zone_trouvee = None
            for zone in zones:
                distance = haversine(
                    float(signalement.latitude), float(signalement.longitude),
                    float(zone.latitude), float(zone.longitude)
                )
                print(distance)
                if distance <= 0.5 : #500 m
                    zone_trouvee = zone
                    break

            if zone_trouvee:
                signalement.zone = zone_trouvee
            try :
                user = User.objects.get(username="user2")
                signalement.utilisateur = user 
                signalement.save()
                print("signalement enregistré avec succés")
            except :
             
                user = User.objects.create(username="user2", password="Abcdefg123@")
                user.save()
                signalement.utilisateur = user 
                signalement.save()
                print("signalement enregistré avec succés")

    return render(request, 'index.html', {'form': form, 'message': message})


#----------------------------------------------------------------------------------------------------------------
# make by kaido alias Architech
# API JSON des images paginées
from django.db.models.functions import TruncDate, ExtractHour
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

# Galerie avec pagination
def galerie(request):
    filtre = request.GET.get('filtre')
    images = Image.objects.all().order_by('-date_upload')
    if filtre in ['pleine', 'vide']:
        images = images.filter(annotation=filtre)

    paginator = Paginator(images, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    return render(request, 'galerie.html', {'images': page_obj})

def change_annotation (request, id):
  
    image = get_object_or_404(Image, id=id)
    # Inverser l'annotation
    image.annotation = "vide" if image.annotation == "pleine" else "pleine"
    print(image.annotation)
    image.save()

    img = Image.objects.all().filter(id=id).values()
    
    return redirect("galerie")

def gallery_items(request):
    images = Image.objects.all().order_by('-date_upload')
    paginator = Paginator(images, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    signalements = Signalement.objects.all()

    adresse = []
    for img in page_obj :
        for s in signalements :
            if img == s.image :
                adresse.append(transforms_adresse(s.adresse))

    data = []
    i = 0
    for img in page_obj:
    
        data.append({
            "id": img.id,
            "nom_fichier": img.nom_fichier,
            "image_url": img.image.url,
            "annotation": img.annotation,
            "date_upload": img.date_upload.strftime("%Y-%m-%d %H:%M"),
            "taille_ko": img.taille_ko,
            "largeur": img.largeur,
            "hauteur": img.hauteur,
            "r_moyen": img.r_moyen,
            "v_moyen": img.v_moyen,
            "b_moyen": img.b_moyen,
            "contraste": img.contraste,
            "adresse" : adresse[i]
        })
        i += 1

    return JsonResponse(data, safe=False)


# cartographie----------------------------------------------------------------
def signalements_items(request):
    signalements = Signalement.objects.all()
    data = []
    data_unique = []
    for s in signalements:
        data.append({
            "lat" : s.latitude,
            "long" : s.longitude
        })

    for i in range(len(data)):
        for j in range(len(data)):
            if data[j] not in data_unique :
                data_unique.append(data[j])
        

    for i in range(len(data_unique)) :
        k = 0
        for j in range(len(data)):
            if data_unique[i] == data[j] :
                k += 1
            
        data_unique[i]["occur"] = k   

    return JsonResponse(data_unique, safe=False)

from statistics import median
def zone_5_view(request):
    signalements = Signalement.objects.all()
    data = []
    data_unique = []
    for s in signalements:
        
        transform_adresse = transforms_adresse(s.adresse)
        data.append({
            "lat" : s.latitude,
            "long" : s.longitude,
            "adresse" : transform_adresse
        })
    
    for i in range(len(data)):
        for j in range(len(data)):
            if contient_adresse(data_unique, data[j]["adresse"]) :
                pass
            else :
                data_unique.append(data[j])
            
            
    for i in range(len(data_unique)) :
        k = 0
        for j in range(len(data)):
            if data_unique[i]["adresse"].replace(" ", "") == data[j]["adresse"].replace(" ", "") :
                k += 1
            
        data_unique[i]["occur"] = k   

    # Tri en ordre croissant selon l'âge
    data_triees = sorted(data_unique, key=lambda p: p["occur"])
    
    return JsonResponse(data_triees[:6:-1], safe=False)

from .models import ClassificationDefine
# Pages simples
def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def classification_rule_view(request):
    rules = ClassificationDefine.objects.all()

    return render(request, 'classification_rule.html', context={"rules" : rules})

def form_rule_view(request):
    form = ClassificationDefineForm()

    if request.method == "POST" :
        form = ClassificationDefineForm(request.POST)
        if form.is_valid :
            form.save()

        redirect("classification_rule")

    return render(request, 'form_rule.html', context={"form" : form})

def activer_rule(request, id) :
    print(id)
    rules = ClassificationDefine.objects.all()

    for r in rules :
        r.active = False
        r.save()

    rule = list(ClassificationDefine.objects.filter(id=id))
    rule = rule[0]
    rule.active = True
    rule.save()

    return redirect("classification_rule")

    


def signalement_view(request):
    return render(request, 'signalement.html')

def acceuil_view(request):
    return render(request, 'acceuil.html')

def cartographie_view(request):
    return render(request, "cartographie.html")


def test_view(request):
    return render(request, 'test.html')


#dashboard

def histogrammes_uploads(request) :
    images_par_jour = list(
        Image.objects
        .annotate(jour=TruncDate("date_upload"))  # Extrait uniquement la date AAAA-MM-JJ
        .values("jour")                             # Regroupe par jour
        .annotate(nb_images=Count("id"))            # Compte les images par jour
        .order_by("jour"))
    
    return JsonResponse(images_par_jour, safe=False)


def histogrammes_hours(request):
    signalements_par_heure = list(
        Image.objects
        .annotate(heure=ExtractHour("date_upload"))  # extrait l'heure (00–23)
        .values("heure")
        .annotate(nb_signalements=Count("id"))
        .order_by("heure")
    )

    return JsonResponse(signalements_par_heure, safe=False)


from .ML import traitement
import time
def analyse_avances(request, filename):

    print(filename)
    image = Image.objects.get(id=filename)
    realname = str(image.image)
    real = realname.split("/")
    real = real[1]
    print(real)
    traitement(real)

    import json
    with open(f"media\\features\\{real}_features.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(data)  # Affiche le contenu sous forme de dictionnaire Python
    return JsonResponse(data, safe=False)


def analyse_avances_view (request,filename) : 
    return render (request, "analyse_avances.html", context= {"filename": filename})


from .models import ZoneRisques
from .forms import ZoneRisquesForm  # À créer

def ajouter_zone_risques(request):
    if request.method == 'POST':
        form = ZoneRisquesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cartographie')  # À adapter
    else:
        form = ZoneRisquesForm()
    return render(request, 'ajouter_zone_risques.html', {'form': form})


def getZones(request) :
    zones = list(ZoneRisques.objects.all())
    data = []
    for z in zones :
        data.append({
            "libelle" : z.libelle,
            "Adresse" : transforms_adresse(z.adresse),
            "latitude" : z.latitude,
            "longitude" : z.longitude,
            "date_debut" : z.date_debut_validite,
            "date_fin" : z.date_fin_validite,
            "occur" : Signalement.objects.filter(zone = z).count()
        })
    return JsonResponse(data, safe=False)



#----------------------------------------------------------------------------------------------------------------------------#
#dashboard card
def stats_globales(request):
    stats = Image.objects.values('annotation').annotate(total=Count('id'))

    total_images = Image.objects.count()
    pleines = stats.filter(annotation='pleine').first()
    videes = stats.filter(annotation='vide').first()

    data = {
        "total": total_images,
        "pleines": pleines["total"] if pleines else 0,
        "videes": videes["total"] if videes else 0
    }
    return JsonResponse(data)

#----------------------------------------------------------------------------------------

def evolution_hebdo(request):
    data = (
        Image.objects
        .annotate(jour=ExtractWeekDay('date_upload'))
        .values('jour', 'annotation')
        .annotate(total=Count('id'))
        .order_by('jour')
    )
    return JsonResponse(list(data), safe=False)


def stats_globales(request):
    total = Image.objects.count()
    pleines = Image.objects.filter(annotation='pleine').count()
    videes = Image.objects.filter(annotation='vide').count()

    return JsonResponse({
        'total': total,
        'pleines': pleines,
        'videes': videes,
    })



def parametres(request):
    """
    Vue pour la page des paramètres
    """
    # Récupérer les statistiques
    total_images = Image.objects.count()
    total_storage = Image.objects.aggregate(total=Sum('taille_ko'))['total'] or 0
    total_storage_gb = round(total_storage / (1024 * 1024), 2)  # Conversion en GB
    
    context = {
        'total_images': total_images,
        'total_storage_gb': total_storage_gb,
    }
    
    return render(request, 'parametres.html', context)


#----------------------------------------------------------
from sklearn.metrics import confusion_matrix
import pandas as pd


def performance_model(request) :
    images = Image.objects.all()
    true_model = 0
    false_model = 0
    test_annotation =  []
    true_annotation = [img.annotation for img in images]
    for image in images :
        features = extract_features(image.image.path,debug=None,filename=image.nom_fichier)
        annotation = classify_trash_can(features)
        if annotation == image.annotation :
            true_model += 1
        else :
            false_model +=1
        
        test_annotation.append(annotation)

    print(true_model)
    print(false_model)
    print(f"pourcentage {true_model/(true_model+false_model)}")

    df_predict = pd.DataFrame({"y_predict" : true_annotation})
    df_test  =  pd.DataFrame({"y_test" : test_annotation})
    
    data = {
        "confusion_matrice" : confusion_matrix(df_test, df_predict).tolist(),
        "precision" : true_model/(true_model+false_model),
        "true_prediction" : true_model,
        "false_prediction" : false_model
    }
    
    return JsonResponse(data)



