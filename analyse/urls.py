from django.urls import path
from . import views

urlpatterns = [
    path('', views.acceuil_view, name='home'),
    path('upload/', views.home, name='upload_image'),
    path('galerie/', views.galerie, name='galerie'),
    path('update_annotation/<int:id>', views.change_annotation),
    path('galerie/data/', views.gallery_items, name='gallery_items'),
    path('avance/<int:filename>', views.analyse_avances, name='avance'),
    path('img_analyse/<int:filename>', views.analyse_avances_view, name='analyse_avancee'),

    # Pages statiques / annexes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('classification_rule/', views.classification_rule_view, name='classification_rule'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('form_rule/', views.form_rule_view, name='form_rule'),
    path('signalement/', views.signalement_view, name='signalement'),
    path("cartographie/", views.cartographie_view, name="cartographie"), 
     
    
    #dashboard and cartographie api
    path("signalements_items/", views.signalements_items, name="signalements_items"),
    path('api/stats-globales/', views.stats_globales, name='stats_globales'),
    path("zone_5/", views.zone_5_view, name="zone_5"),
    path("histogrammes_uploads/", views.histogrammes_uploads, name="histogramme"),
    path("histogrammes_hours/", views.histogrammes_hours, name="histogramme_hour"),
    path('parametres/', views.parametres, name='parametres'),


    path("ajouter_zone_risque", views.ajouter_zone_risques, name="liste_zones_risques"),
    path("getZones/", views.getZones, name="getZones"),
    path("performance/", views.performance_model, name="performance"),
    path("activer/<int:id>", views.activer_rule),
    path("tester/", views.test_view, name="test")

]


