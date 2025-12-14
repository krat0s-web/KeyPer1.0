# Déploiement KeyPer sur PythonAnywhere (100% GRATUIT!)

**PythonAnywhere est GRATUIT - Aucune carte de crédit requise!**

## Avantages
✅ Gratuit sans limite de durée
✅ Pas de carte de crédit
✅ PostgreSQL gratuit
✅ SSL/HTTPS gratuit
✅ Support Django natif
✅ Interface web pour tout gérer

## Étapes

### 1. S'enregistrer sur PythonAnywhere
- Aller sur https://www.pythonanywhere.com
- Cliquer "Sign up for a free account"
- Créer un compte avec ton email

### 2. Créer une app Web
1. Aller à l'onglet "Web"
2. Cliquer "Add a new web app"
3. Choisir:
   - Domaine: `votrenonutilisateur.pythonanywhere.com` (gratuit)
   - Framework: **Manual configuration**
   - Python version: **3.11**

### 3. Charger ton code

#### Option A: Via Git (recommandé)
```bash
# Dans le terminal PythonAnywhere
git clone https://github.com/VOTRE_USERNAME/KeyPer.git
```

#### Option B: Upload ZIP
1. Télécharger le code en ZIP
2. Uploader dans PythonAnywhere

### 4. Configurer l'environnement virtuel

Dans le terminal PythonAnywhere:
```bash
# Aller dans le dossier
cd ~/KeyPer

# Créer virtualenv
mkvirtualenv --python=/usr/bin/python3.11 keyper

# Installer les dépendances
pip install -r requirements.txt
```

### 5. Configurer la base de données

#### Option A: PostgreSQL gratuit (recommandé)
PythonAnywhere offre PostgreSQL gratuit! Sinon utiliser SQLite.

Dans settings_production.py, PostgreSQL est déjà configuré.

#### Option B: SQLite (plus simple)
```python
# Modifier settings_production.py pour utiliser SQLite en prod si tu veux
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

### 6. Configurer la web app

1. PythonAnywhere > Web > ton app
2. Source code: `/home/VOTREUSERNAME/KeyPer`
3. Working directory: `/home/VOTREUSERNAME/KeyPer`
4. WSGI configuration file: `/home/VOTREUSERNAME/KeyPer/gestion_taches_project/wsgi.py`

**Éditer le WSGI file:**
```python
import os
import sys

path = '/home/VOTREUSERNAME/KeyPer'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'gestion_taches_project.settings_production'

# Variables d'environnement
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'VOTREUSERNAME.pythonanywhere.com'
os.environ['SECRET_KEY'] = 'GENERE-UNE-CLE-SECRETE'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 7. Configurer les variables d'environnement

PythonAnywhere > Web > Environment variables
```
DJANGO_SETTINGS_MODULE=gestion_tacles_project.settings_production
DEBUG=False
SECRET_KEY=<générer: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=VOTREUSERNAME.pythonanywhere.com
```

### 8. Migrations et static files

Dans le terminal PythonAnywhere:
```bash
# Migrations
python manage.py migrate

# Fichiers statiques
python manage.py collectstatic --noinput
```

### 9. Redémarrer l'app
1. PythonAnywhere > Web > Reload web app
2. OU cliquer le bouton vert "Reload"

### 10. Accéder au site
```
https://VOTREUSERNAME.pythonanywhere.com
```

## Commandes utiles

```bash
# Dans le terminal PythonAnywhere
# Activer l'environnement virtuel
workon keyper

# Shell Django
python manage.py shell

# Créer superuser
python manage.py createsuperuser

# Migrations
python manage.py migrate

# Static files
python manage.py collectstatic
```

## Limites gratuites PythonAnywhere
- ✅ 1 app web
- ✅ 100 MB espace disque
- ✅ PostgreSQL gratuit
- ✅ SSL/HTTPS gratuit
- ✅ Pas de limite de visites
- ⚠️ CPU limité (OK pour petit projet)
- ⚠️ Arrêt après 3 mois d'inactivité

## Dépannage

### "ModuleNotFoundError: No module named 'django'"
- Vérifier que pip install a bien installé les dépendances
- Vérifier que le virtualenv est actif
- Relancer: `pip install -r requirements.txt`

### "Database connection error"
- Vérifier DATABASE_URL ou configuration
- Pour SQLite, vérifier chemin absolu
- Relancer migrations: `python manage.py migrate`

### 502 Bad Gateway
- Vérifier les logs PythonAnywhere (Web > Errors)
- Vérifier WSGI file est correct
- Cliquer Reload

### "Static files not found"
- Lancer: `python manage.py collectstatic --noinput`
- Vérifier STATIC_ROOT dans settings
- Relancer l'app

## Upgrade futur
Si tu besoins plus:
- Plan Beginner: $5/mois (200MB, meilleure performance)
- Plan Pro: $50/mois (1GB, plusieurs apps)

Mais le plan gratuit est suffisant pour tester!

## Étapes résumées

1. ✅ S'inscrire: https://www.pythonanywhere.com
2. ✅ Add web app > Manual configuration
3. ✅ Clone le repo Git
4. ✅ Installer requirements.txt
5. ✅ Configurer WSGI file
6. ✅ Faire les migrations
7. ✅ Collecte les static files
8. ✅ Reload
9. ✅ C'est en ligne! 🎉

## Support
- Docs: https://www.pythonanywhere.com/help/
- Chat support: 24/7 gratuit
- Forums: https://www.pythonanywhere.com/forums/

**Besoin d'aide? Les admins PythonAnywhere sont très réactifs!**
