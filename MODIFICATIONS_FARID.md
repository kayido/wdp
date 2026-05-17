# Passation - travail branche `farid-codex-work`

Ce document résume les changements faits depuis la branche `main` afin que le groupe puisse relire, tester et reprendre facilement.

## Objectif de la branche

La branche améliore le projet Wild Dump Prevention autour de deux axes :

- séparer les usages entre utilisateur lambda et administrateur ;
- moderniser le parcours utilisateur côté citoyen sans casser le fonctionnement existant.

Le principe fonctionnel retenu est le suivant :

- utilisateur lambda : collecte terrain, upload d'image, adresse/localisation, commentaire ;
- administrateur : consultation, annotation, correction, dashboard, cartographie, règles de classification.

## Changements principaux

### 1. Séparation lambda / admin

Fichiers concernés :

- `analyse/access.py`
- `analyse/views.py`
- `analyse/urls.py`
- `analyse/templates/components/navbar.html`
- `analyse/templates/login.html`
- `analyse/templates/register.html`

Ce qui a été fait :

- ajout d'un fichier `analyse/access.py` pour centraliser les règles d'accès ;
- protection des pages admin avec `is_staff` et permissions Django ;
- ajout d'un parcours simple `register`, `login`, `logout` pour les utilisateurs lambda ;
- l'utilisateur lambda ne doit pas accéder à l'annotation, au dashboard ou à la cartographie admin ;
- les administrateurs conservent l'accès aux pages de pilotage.

Permissions utilisées :

- `analyse.view_image`
- `analyse.change_image`
- `analyse.view_signalement`
- `analyse.view_zonerisques`
- `analyse.add_zonerisques`
- `analyse.view_classificationdefine`
- `analyse.add_classificationdefine`
- `analyse.change_classificationdefine`

### 2. Upload et traçabilité

Fichiers concernés :

- `analyse/views.py`
- `analyse/templates/index.html`
- `analyse/static/analyse/index.css`
- `analyse/static/js/index.js`

Ce qui a été fait :

- le signalement est rattaché à l'utilisateur connecté quand il existe ;
- si l'utilisateur n'est pas connecté, le signalement est rattaché à `anonymous_reporter` ;
- le formulaire de signalement a été réorganisé visuellement en étapes : photo, localisation, détails ;
- le champ adresse est plus lisible ;
- le placeholder d'adresse est générique : `Ex : Avenue de la République` ;
- l'autocomplétion adresse et la géolocalisation ont été améliorées côté JavaScript ;
- une confirmation est affichée après l'envoi du signalement.

Important :

- le champ adresse reste critique pour la soutenance, il faut le tester manuellement.

### 3. Interface publique

Fichiers concernés :

- `analyse/templates/acceuil.html`
- `analyse/static/analyse/acceuil.css`
- `analyse/static/analyse/navbar.css`
- `analyse/templates/components/navbar.html`

Ce qui a été fait :

- modernisation de l'accueil public ;
- direction plus sobre, plus minimaliste et plus civic-tech ;
- suppression du faux composant carte/localisation dans le hero ;
- CTA principal orienté vers le signalement ;
- affichage adapté selon utilisateur lambda ou admin ;
- navbar modernisée sans changer les routes.

### 4. Login / register

Fichiers concernés :

- `analyse/templates/login.html`
- `analyse/templates/register.html`
- `analyse/static/analyse/login.css`

Ce qui a été fait :

- pages de connexion et création de compte rendues plus propres visuellement ;
- parcours simple suffisant pour une démonstration ;
- les comptes créés via `/register/` sont des utilisateurs lambda non staff.

### 5. Nettoyage technique et corrections

Fichiers concernés :

- `.gitignore`
- `requirements.txt`
- `analyse/forms.py`
- `analyse/apps.py`
- `analyse/signals.py`
- `analyse/views.py`
- `analyse/static/js/cartographie.js`
- `analyse/static/js/dashboard.js`

Ce qui a été fait :

- ajout de dépendances Python manquantes ;
- nettoyage des fichiers `__pycache__` suivis par Git ;
- ajout d'un `.gitignore` plus propre ;
- correction de `form_rule_view()` avec `form.is_valid()` ;
- correction de redirections et URLs relatives côté JavaScript ;
- activation des signaux via `AnalyseConfig.ready()` ;
- durcissement de l'extraction de features pour éviter les erreurs OpenCV sur certains uploads.

### 6. Documentation

Fichiers concernés :

- `README.md`
- `MODIFICATIONS_FARID.md`

Ce qui a été fait :

- README réécrit pour la soutenance ;
- ajout des objectifs, installation, lancement, workflow, rôles, URLs de démo ;
- ajout des limites connues ;
- ajout d'une section Green IT ;
- ajout des tests manuels recommandés ;
- création de ce fichier de passation.

### 7. Tests

Fichier concerné :

- `analyse/tests.py`

Les tests couvrent notamment :

- chargement des pages publiques ;
- redirection des pages admin pour utilisateurs anonymes ;
- accès admin pour superuser ;
- refus d'un staff sans permission ;
- accès dashboard pour un staff avec permission ;
- workflow upload avec nom de fichier accentué ;
- rattachement upload connecté à l'utilisateur courant ;
- rattachement upload anonyme à `anonymous_reporter` ;
- register/login lambda ;
- APIs dashboard et cartographie ;
- protection de l'annotation ;
- création d'une règle de classification ;
- cohérence du formulaire `ClassificationDefineForm` ;
- enregistrement du signal d'extraction de features.

## Commandes de vérification

À lancer avant merge :

```powershell
python manage.py check
python manage.py test
```

Résultat obtenu localement avant push :

- `python manage.py check` : OK ;
- `python manage.py test` : 18 tests OK.

## Tests manuels à faire par le groupe

### Parcours lambda

1. Ouvrir `/`.
2. Ouvrir `/register/`.
3. Créer un compte non admin.
4. Aller sur `/upload/`.
5. Envoyer une image avec adresse et commentaire.
6. Vérifier la confirmation.
7. Vérifier que `/dashboard/`, `/galerie/`, `/cartographie/` ne sont pas accessibles.

### Champ adresse

1. Taper une adresse.
2. Effacer.
3. Retaper une autre adresse.
4. Vérifier que les suggestions reviennent.
5. Tester le bouton de géolocalisation si le navigateur le permet.

### Parcours admin

1. Se connecter avec un superuser.
2. Ouvrir `/galerie/`.
3. Vérifier que les images uploadées apparaissent.
4. Tester la correction annotation pleine/vide.
5. Ouvrir `/dashboard/`.
6. Ouvrir `/cartographie/`.
7. Ouvrir `/classification_rule/`.

## Fichiers à ne pas pousser par erreur

Ne pas committer :

- `db.sqlite3` si elle contient seulement des données locales de test ;
- les fichiers uploadés dans `media/uploads/` créés pendant les essais ;
- les fichiers générés dans `__pycache__/`.

## Points d'attention avant merge

- La branche est fonctionnelle localement, mais il faut valider visuellement l'UI sur plusieurs tailles d'écran.
- Le fichier `views.py` reste volumineux : il fonctionne, mais un découpage pourra être fait plus tard.
- Le système login/register reste simple et adapté à une démo, pas à une production.
- La cartographie et l'autocomplétion d'adresse peuvent dépendre d'un accès Internet.
- Les médias et la base SQLite doivent être gérés avec prudence avant un merge final.

## Résumé rapide pour la soutenance

La contribution principale est d'avoir transformé l'application en deux parcours plus clairs :

- le citoyen signale une poubelle avec photo, localisation et commentaire ;
- l'administrateur valide, corrige, analyse et pilote les données.

Cette séparation rend le projet plus crédible pour une démonstration, plus clair pour les utilisateurs, et plus cohérent avec le cahier des charges.
