# Déploiement KeyPer sur Render

## Étapes rapides

### 1. Préparer le code
```bash
git add .
git commit -m "Préparation pour déploiement Render"
git push origin main
```

### 2. Créer un compte Render
- Aller sur https://render.com
- S'enregistrer avec GitHub

### 3. Créer l'app sur Render

#### A. Créer la base de données PostgreSQL
1. Dashboard Render > New > PostgreSQL
2. Name: `keyper-db`
3. Region: `Frankfurt (EU)`
4. Plan: `Standard` (gratuit avec limites)
5. Créer et noter les credentials

#### B. Créer l'app Web
1. Dashboard Render > New > Web Service
2. Connecter le repository GitHub
3. Configurer:
   - **Name**: `keyper`
   - **Environment**: `Python 3`
   - **Region**: `Frankfurt (EU)`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command**: `gunicorn gestion_tacles_project.wsgi:application --bind 0.0.0.0:$PORT`

### 4. Configurer les variables d'environnement (Environment)
Dans Render, aller à l'app > Environment

```
DJANGO_SETTINGS_MODULE=gestion_tacles_project.settings_production
DEBUG=False
SECRET_KEY=<générer avec: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=<votre-domaine-render>.onrender.com

# PostgreSQL (copier depuis la base de données créée)
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>

# Ou individuellement:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<nom_base>
DB_USER=<user>
DB_PASSWORD=<password>
DB_HOST=<host>
DB_PORT=5432

# HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<votre_email>
EMAIL_HOST_PASSWORD=<votre_app_password>
DEFAULT_FROM_EMAIL=<votre_email>
```

### 5. Déployer
- Render déploiera automatiquement à chaque push sur `main`
- Ou cliquer sur "Deploy latest commit" dans Render

## Vérification après déploiement

```bash
# Vérifier les logs
# Render > votre app > Logs

# Vérifier que les migrations ont roulé
# Les tables doivent être créées dans PostgreSQL

# Créer un superuser en production
# (Si nécessaire)
```

## Dépannage

### Build fails
- Vérifier les logs Render
- Vérifier que `requirements.txt` est à jour
- Vérifier les secrets dans Environment

### "Internal Server Error"
- Vérifier DEBUG=False
- Vérifier les logs de l'app
- Vérifier que ALLOWED_HOSTS inclut votre domaine

### Base de données vide
- Vérifier que les migrations ont roulé
- Vérifier DATABASE_URL est correct

## Points importants

⚠️ **SÉCURITÉ**:
- Jamais commiter `.env` ou secrets
- Régénérer SECRET_KEY
- Utiliser HTTPS (automatique sur Render)
- SECURE_SSL_REDIRECT=True
- Activer l'authentification forte

✅ **PRODUCTION**:
- DEBUG=False toujours
- ALLOWED_HOSTS configuré
- PostgreSQL en production
- Sauvegardes régulières
- Monitoring des logs

## Coûts Render (estimés)
- Web service: ~$12/mois (gratuit pour 0.1 CPU)
- PostgreSQL: ~$7/mois (gratuit avec limites)

## Support
- Docs Render: https://render.com/docs
- Django deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
