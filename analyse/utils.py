# analyse/utils.py

import datetime as dt
import requests
from django.db.models import Count
from django.utils import timezone

from .models import Signalement

# URL de l'API météo gratuite Open-Meteo
OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}&daily=weathercode&timezone=Europe%2FParis"
)

def meteo_ensoleillee(lat, lon):
    """
    Renvoie True si la météo de demain est ensoleillée (codes 0 à 2).
    """
    url = OPEN_METEO_URL.format(lat=lat, lon=lon)
    try:
        response = requests.get(url, timeout=5)
        code = response.json()["daily"]["weathercode"][0]
        return code in (0, 1, 2)  # 0–2 = ciel clair / peu nuageux
    except Exception as e:
        print(f"[WARN] Erreur météo : {e}")
        return False  # prudence : pas de réseau → on ne surestime pas


def transforms_adresse(c_adresse):
    adresse = c_adresse.split(',')
    try : 
        transform_adresse = (adresse[0] if not isinstance(int(adresse[0]), int) else "")+ adresse[1] +" "+adresse[2] +" " + adresse[len(adresse)-2]
    except :
        transform_adresse = (adresse[0] if not isinstance(adresse[0], int) else "")+ adresse[1] + " " + adresse[len(adresse)-2]

    return transform_adresse


def contient_adresse(tableau, valeur_recherchee):
    for element in tableau:
        if element.get("adresse").replace(" ", "") == valeur_recherchee.replace(" ", ""):
            return True
    return False



from math import radians, cos, sin, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Rayon de la Terre en km
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # en km



