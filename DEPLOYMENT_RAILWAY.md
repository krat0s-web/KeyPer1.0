# Déploiement KeyPer sur Railway (GRATUIT!)

Railway est **100% gratuit** pour les petits projets avec $5/mois de crédit gratuit!

## Étapes rapides

### 1. S'enregistrer sur Railway
- Aller sur https://railway.app
- Cliquer "Sign Up"
- Signer avec GitHub (le plus simple)

### 2. Créer un nouveau projet
1. Dashboard > New Project
2. "Deploy from GitHub repo"
3. Connecter ton repository
4. Sélectionner le repo KeyPer

### 3. Configuration automatique
Railway détecte Django automatiquement et crée:
- Une app Python
- Une PostgreSQL database

### 4. Configurer les variables d'environnement

Dans Railway > ton projet > Variables:

```
DJANGO_SETTINGS_MODULE=gestion_tacles_project.settings_production
DEBUG=False
SECRET_KEY=<générer: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=*

# Database (Railway génère automatiquement DATABASE_URL)
# Laisse DATABASE_URL vide, Railway le fait pour toi

# HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 5. Deploy
- Railway déploie automatiquement
- Vérifier les logs pour erreurs
- L'URL du site apparaît dans Railway

## Variables d'environnement importants

Railway crée automatiquement `DATABASE_URL` - elle est déjà configurée dans settings_production.py!

Si Railway demande d'autres variables, les ajouter dans Railway > Variables.

## Accéder au site en production

L'URL sera quelque chose comme:
```
https://keyper-production-xxxx.railway.app
```

## Commandes utiles (depuis Railway terminal)

```bash
# Voir les logs
railway logs

# Shell Django
railway run python manage.py shell

# Créer un superuser
railway run python manage.py createsuperuser

# Migrer la DB manuellement
railway run python manage.py migrate
```

## Limites gratuites Railway
- $5/mois de crédit gratuit
- Assez pour une petite app + PostgreSQL
- Pas de limite de visites
- Arrêt après 72h d'inactivité (redémarre automatiquement)

## Dépannage

### "Cannot import settings_production"
- Vérifier `DJANGO_SETTINGS_MODULE` est correctement orthographié
- Vérifier le fichier existe: `gestion_tacles_project/settings_production.py`

### "Database connection error"
- Railway crée DATABASE_URL automatiquement
- Elle s'ajoute dans Railway > Variables
- Pas besoin de la configurer manuellement

### "Static files not found"
- Les fichiers statiques sont collectés automatiquement par Gunicorn + WhiteNoise
- Pas d'action nécessaire

### "Internal Server Error"
- Voir les logs Railway
- Vérifier DEBUG=False
- Vérifier ALLOWED_HOSTS inclut le domaine Railway

## Monitoring

Railway te montre automatiquement:
- CPU/Memory usage
- Logs en temps réel
- Erreurs de deployment
- Coûts (gratuit jusqu'à $5/mois)

## Upgrade futur
Si tu dépassses $5/mois, Railway arrête simplement le service (pas de surprise).
Tu peux ajouter une carte de crédit pour continuer ou optimiser l'app.

## Support
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Docs Django deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
