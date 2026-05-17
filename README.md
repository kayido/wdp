# Wild Dump Prevention

Wild Dump Prevention est une plateforme web Django destinée à suivre l'état des poubelles à partir d'images afin d'aider à prévenir les dépôts sauvages.

Le projet permet d'uploader des images, d'extraire automatiquement des caractéristiques simples, de classifier l'état d'une poubelle avec des règles conditionnelles, puis de visualiser les résultats dans une galerie, un dashboard et une cartographie.

## Objectifs

- Centraliser des images de poubelles signalées.
- Séparer les usages entre collecte terrain et administration.
- Annoter ou corriger l'état des poubelles côté administrateur.
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

## Rôles et accès

Le projet utilise les droits standards Django pour séparer les usages :

- utilisateur lambda : accès à l'accueil et au formulaire de signalement ;
- administrateur/superuser : accès à toutes les pages de pilotage ;
- staff avec permissions fines : accès limité selon les permissions Django associées.

L'utilisateur lambda sert principalement à collecter la donnée terrain. Il peut envoyer une image, ajouter une adresse si disponible, ajouter un commentaire optionnel, puis recevoir une confirmation. La création de compte public a été retirée car elle n'apporte pas de valeur fonctionnelle pour la démonstration actuelle.

Un signalement public est rattaché au compte système `anonymous_reporter`. Si un administrateur envoie un signalement en étant connecté, il est rattaché à son compte.

Les pages admin sont protégées par `is_staff` et par des permissions Django dans `analyse/access.py` :

- `analyse.view_image` : galerie, dashboard, statistiques et analyses image ;
- `analyse.change_image` : correction d'annotation ;
- `analyse.view_signalement` : cartographie et signalements ;
- `analyse.view_zonerisques` / `analyse.add_zonerisques` : zones à risque ;
- `analyse.view_classificationdefine`, `add_classificationdefine`, `change_classificationdefine` : règles de classification.

Pour créer un compte administrateur local :

```powershell
python manage.py createsuperuser
```

## URLs utiles pour la démonstration

- Accueil public : `http://127.0.0.1:8000/`
- Signalement public : `http://127.0.0.1:8000/upload/`
- Connexion administrateur : `http://127.0.0.1:8000/login/`
- Déconnexion : `http://127.0.0.1:8000/logout/`
- Admin Django : `http://127.0.0.1:8000/admin/`
- Galerie admin : `http://127.0.0.1:8000/galerie/`
- Dashboard admin : `http://127.0.0.1:8000/dashboard/`
- Cartographie admin : `http://127.0.0.1:8000/cartographie/`
- Règles de classification admin : `http://127.0.0.1:8000/classification_rule/`

## Interface utilisateur actuelle

L'interface publique a été orientée vers un parcours citoyen simple :

- une page d'accueil plus minimaliste et éditoriale ;
- un message principal centré sur l'action : signaler une poubelle ;
- un formulaire de signalement organisé par étapes : photo, localisation, détails ;
- un champ adresse large et lisible avec un placeholder générique : `Ex : Avenue de la République` ;
- une aide à la localisation via recherche d'adresse et géolocalisation navigateur ;
- une confirmation visible après l'envoi d'un signalement ;
- une connexion dédiée aux administrateurs.

La page d'accueil ne contient plus de faux composant de carte ou d'adresse personnelle d'exemple. Les adresses affichées dans l'interface doivent rester génériques afin d'éviter d'utiliser des données personnelles ou trop réalistes dans la démonstration.

Le parcours utilisateur lambda reste volontairement limité : il collecte la donnée terrain, mais ne peut pas annoter les images. L'annotation, la correction, le dashboard et la cartographie restent réservés aux administrateurs.

## Workflow applicatif

1. L'utilisateur envoie une image depuis la page de signalement, sans création de compte.
2. Il ajoute une adresse, utilise la géolocalisation si nécessaire, et peut compléter avec un commentaire.
3. L'image est stockée dans `media/uploads/`.
4. Le système extrait des caractéristiques simples : dimensions, taille, couleur moyenne, luminance, contraste et histogramme.
5. Des caractéristiques plus avancées sont calculées dans `analyse/ML.py` : contours, densité de bords, saturation, zones de l'image et texture.
6. La fonction de classification applique des règles conditionnelles configurables.
7. Le signalement est enregistré avec l'image, le commentaire, l'utilisateur système anonyme et les informations de localisation si disponibles.
8. Un administrateur se connecte, consulte la galerie, annote ou corrige l'état pleine/vide.
9. Le dashboard affiche les statistiques globales.
10. La cartographie affiche les signalements et les zones à risque.

## Principaux fichiers

- `analyse/models.py` : modèles de données principaux.
- `analyse/access.py` : règles d'accès staff et permissions fines.
- `analyse/views.py` : vues Django, APIs JSON et logique métier.
- `analyse/ML.py` : extraction de caractéristiques et classification par règles.
- `analyse/forms.py` : formulaires d'upload, règles et zones à risque.
- `analyse/templates/` : pages HTML.
- `analyse/static/` : fichiers CSS et JavaScript.
- `analyse/tests.py` : tests de non-régression.
- `accounts/views.py` : vues de connexion, déconnexion et redirection d'inscription.
- `accounts/urls.py` : routes d'authentification `/login/`, `/logout/` et `/register/`.
- `accounts/templates/accounts/` : templates de connexion admin.
- `media/uploads/` : images de démonstration et images uploadées.
- `media/features/` : fichiers JSON de caractéristiques avancées.

## Points d'attention UI/UX

- Le design public doit rester sobre et centré sur la contribution citoyenne.
- Les composants trop artificiels ou les fausses cartes décoratives sont à éviter.
- Les exemples d'adresse doivent rester génériques.
- Le champ adresse est critique pour la valeur métier du projet : il faut vérifier l'autocomplétion, l'effacement/re-saisie et la géolocalisation avant la soutenance.
- Le responsive mobile doit être testé, car le signalement peut être réalisé depuis un téléphone.

## Tests manuels recommandés

Avant la démo, tester les parcours suivants dans le navigateur :

1. Parcours anonyme :
   - ouvrir `http://127.0.0.1:8000/` ;
   - vérifier que seuls les liens publics sont visibles ;
   - ouvrir `/upload/` ;
   - envoyer une image avec ou sans adresse ;
   - vérifier que le placeholder d'adresse reste générique ;
   - tester l'effacement et la nouvelle saisie dans le champ adresse ;
   - tester le bouton de géolocalisation si le navigateur le permet ;
   - vérifier le message de confirmation ;
   - essayer `/dashboard/` et vérifier la redirection vers la connexion admin.

2. Parcours connexion admin :
   - ouvrir `/login/` ;
   - vérifier qu'un compte non staff ne peut pas se connecter ;
   - se connecter avec un compte administrateur ;
   - vérifier que la navbar affiche `Déconnexion` et les liens admin.

3. Parcours administrateur :
   - ouvrir `/admin/` et se connecter avec un superuser ;
   - ouvrir `/galerie/` ;
   - vérifier que les nouvelles images apparaissent ;
   - cliquer sur le changement d'annotation ;
   - ouvrir `/dashboard/` et vérifier les graphiques ;
   - ouvrir `/cartographie/` et vérifier les points de signalement ;
   - ouvrir `/classification_rule/` et vérifier les règles.

4. Permissions fines :
   - créer un utilisateur `is_staff` non superuser dans `/admin/` ;
   - sans permission, vérifier qu'il ne peut pas ouvrir `/dashboard/` ;
   - lui ajouter `analyse | image | Can view image` ;
   - vérifier qu'il peut ouvrir `/dashboard/`, mais pas forcément corriger une annotation sans `Can change image`.

5. Vérification technique :
   - ouvrir la console navigateur ;
   - vérifier qu'il n'y a pas d'erreurs rouges sur dashboard/cartographie ;
   - vérifier `git status` pour ne pas committer `db.sqlite3` ou des uploads de test par erreur.

## Captures à prévoir pour la soutenance

Les captures ne sont pas incluses dans ce README. Pour la soutenance, prévoir idéalement :

- page d'accueil publique ;
- formulaire de signalement avec prévisualisation, champ adresse et commentaire ;
- redirection vers la connexion admin lorsqu'un utilisateur non staff tente d'accéder au dashboard ;
- galerie admin avec annotations ;
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
- La page login est réservée aux administrateurs ; la création de compte public est désactivée.
- Les résultats de classification restent dépendants des règles et de la qualité des images.
- Les médias de démonstration et la base SQLite sont encore présents dans le dépôt.
- Certaines fonctionnalités cartographiques dépendent d'OpenStreetMap/Nominatim et nécessitent Internet.
- `views.py` reste volumineux ; la logique d'accès a été séparée dans `analyse/access.py` et l'authentification dans `accounts`, mais un découpage complet des vues pourra être fait plus tard.

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

## Tests automatisés

Les tests du projet sont principalement dans `analyse/tests.py`. Les tests d'authentification sont dans `accounts/tests.py`.

Ils couvrent actuellement :

- le chargement des pages publiques ;
- la redirection des pages admin pour les utilisateurs anonymes ;
- l'accès aux pages admin pour un superuser ;
- le refus d'un staff sans permission fine ;
- l'accès dashboard pour un staff avec `view_image` ;
- le workflow d'upload avec un nom de fichier accentué ;
- le rattachement d'un upload connecté à l'utilisateur courant ;
- le rattachement d'un upload anonyme au compte système `anonymous_reporter` ;
- le refus de connexion pour un utilisateur non staff ;
- la connexion d'un administrateur ;
- les APIs utilisées par le dashboard et la cartographie ;
- l'impossibilité de modifier une annotation sans droit admin ;
- la création d'une règle de classification via `/form_rule/` ;
- la cohérence du formulaire `ClassificationDefineForm` ;
- l'enregistrement du signal d'extraction de caractéristiques des images.

Ces tests servent de filet de sécurité après les nettoyages techniques, les corrections de routes et la séparation des droits utilisateur/admin.
