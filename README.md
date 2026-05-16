# Wild Dump Prevention

Wild Dump Prevention est une plateforme web Django destinée à suivre l'état des poubelles à partir d'images afin d'aider à prévenir les dépôts sauvages.

Le projet permet d'uploader des images, d'extraire automatiquement des caractéristiques simples, de classifier l'état d'une poubelle avec des règles conditionnelles, puis de visualiser les résultats dans une galerie, un dashboard et une cartographie.

## Objectifs

- Centraliser des images de poubelles signalées.
- Annoter ou corriger l'état des poubelles.
- Extraire des caractéristiques visuelles simples : taille du fichier, dimensions, couleur moyenne, luminance, contraste, histogrammes et contours.
- Classifier les images avec une logique de règles configurable.
- Visualiser les statistiques dans un dashboard.
- Identifier des zones à risque sur une carte.
- Présenter une approche sobre et explicable, compatible avec une démarche Green IT.

## Installation

Cloner le projet puis se placer dans le dossier :

```powershell
cd wdp
```

Créer et activer un environnement virtuel :

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Installer les dépendances :

```powershell
pip install -r requirements.txt
```

Vérifier la configuration Django :

```powershell
python manage.py check
```

## Lancement

Démarrer le serveur local :

```powershell
python manage.py runserver
```

Puis ouvrir :

```txt
http://127.0.0.1:8000/
```

## URLs utiles pour la démonstration

- Accueil : `http://127.0.0.1:8000/`
- Upload : `http://127.0.0.1:8000/upload/`
- Galerie : `http://127.0.0.1:8000/galerie/`
- Dashboard : `http://127.0.0.1:8000/dashboard/`
- Cartographie : `http://127.0.0.1:8000/cartographie/`
- Règles de classification : `http://127.0.0.1:8000/classification_rule/`

## Workflow applicatif

1. L'utilisateur upload une image depuis la page Upload.
2. L'image est stockée dans `media/uploads/`.
3. Le système extrait des caractéristiques simples : dimensions, taille, couleur moyenne, luminance, contraste et histogramme.
4. Des caractéristiques plus avancées sont calculées dans `analyse/ML.py` : contours, densité de bords, saturation, zones de l'image et texture.
5. La fonction de classification applique des règles conditionnelles configurables.
6. L'image apparaît dans la galerie avec son état estimé.
7. L'utilisateur peut corriger l'annotation.
8. Le dashboard affiche les statistiques globales.
9. La cartographie affiche les signalements et les zones à risque.

## Principaux fichiers

- `analyse/models.py` : modèles de données principaux.
- `analyse/views.py` : vues Django, APIs JSON et logique de pages.
- `analyse/ML.py` : extraction de caractéristiques et classification par règles.
- `analyse/forms.py` : formulaires d'upload, règles et zones à risque.
- `analyse/templates/` : pages HTML.
- `analyse/static/` : fichiers CSS et JavaScript.
- `media/uploads/` : images de démonstration et images uploadées.
- `media/features/` : fichiers JSON de caractéristiques avancées.

## Captures à prévoir pour la soutenance

Les captures ne sont pas incluses dans ce README. Pour la soutenance, prévoir idéalement :

- page d'accueil ;
- formulaire d'upload avec prévisualisation ;
- galerie avec annotations ;
- page d'analyse avancée ;
- dashboard avec graphiques ;
- cartographie avec points de signalement.

## Démarche Green IT

Le projet adopte une approche légère :

- classification par règles plutôt qu'un modèle profond coûteux ;
- extraction de caractéristiques simples et explicables ;
- conversion des images en WebP pour réduire le poids de stockage ;
- suppression prévue des anciennes images via une tâche planifiée ;
- usage de SQLite en environnement local pour limiter la complexité.

Cette approche favorise la sobriété, l'explicabilité et une consommation raisonnable des ressources.

## Limites connues

- Le projet est conçu pour une démonstration locale, pas pour une mise en production directe.
- `DEBUG=True` et la clé secrète Django sont encore dans `settings.py`.
- Les pages login/register existent mais ne portent pas encore une authentification complète.
- Les résultats de classification restent dépendants des règles et de la qualité des images.
- Les médias de démonstration et la base SQLite sont encore présents dans le dépôt.
- Certaines fonctionnalités cartographiques dépendent d'OpenStreetMap/Nominatim et nécessitent Internet.

## Commandes utiles

Lancer les vérifications Django :

```powershell
python manage.py check
```

Lancer les tests :

```powershell
python manage.py test
```

Vérifier les fichiers ignorés par Git :

```powershell
git status --ignored
```

## Tests automatises

Les tests du projet sont dans `analyse/tests.py`.

Ils couvrent actuellement :

- le chargement des pages principales ;
- le workflow d'upload avec un nom de fichier accentué ;
- l'API `/api/stats-globales/` utilisée par le dashboard ;
- la création d'une règle de classification via `/form_rule/` ;
- la cohérence du formulaire `ClassificationDefineForm` ;
- l'enregistrement du signal d'extraction de caractéristiques des images.

Ces tests servent surtout de filet de sécurité après les nettoyages techniques et les corrections de routes.
