# Guide de Déploiement - KeyPer

Ce guide vous aidera à déployer l'application KeyPer en production.

## 📋 Prérequis

- Python 3.8 ou supérieur
- PostgreSQL (recommandé) ou SQLite (pour les petits déploiements)
- Serveur web (Nginx recommandé)
- Serveur WSGI (Gunicorn recommandé)
- Domaine avec certificat SSL (recommandé)

## 🚀 Étapes de Déploiement

### 1. Préparation de l'environnement

```bash
# Cloner le projet
git clone <votre-repo>
cd KeyPer

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration de la base de données

#### Option A : PostgreSQL (Recommandé pour la production)

```bash
# Installer PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian

# Créer la base de données
sudo -u postgres psql
CREATE DATABASE keyper_db;
CREATE USER keyper_user WITH PASSWORD 'votre-mot-de-passe';
GRANT ALL PRIVILEGES ON DATABASE keyper_db TO keyper_user;
\q
```

#### Option B : SQLite (Pour les petits déploiements)

SQLite est déjà configuré par défaut. Assurez-vous que le fichier `db.sqlite3` est dans un répertoire sécurisé.

### 3. Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos valeurs réelles
nano .env
```

**IMPORTANT** : Ne commitez JAMAIS le fichier `.env` avec des valeurs réelles !

### 4. Génération de la clé secrète

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiez la clé générée dans votre fichier `.env` comme valeur de `SECRET_KEY`.

### 5. Configuration Django pour la production

Le fichier `settings_production.py` est déjà configuré. Pour l'utiliser :

```bash
# Option 1 : Variable d'environnement
export DJANGO_SETTINGS_MODULE=gestion_taches_project.settings_production

# Option 2 : Modifier wsgi.py
# Dans gestion_taches_project/wsgi.py, changez :
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_taches_project.settings_production')
```

### 6. Migrations de la base de données

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### 7. Collecte des fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 8. Configuration du serveur WSGI (Gunicorn)

```bash
# Installer Gunicorn (déjà dans requirements.txt)
pip install gunicorn

# Tester Gunicorn
gunicorn gestion_taches_project.wsgi:application --bind 0.0.0.0:8000
```

### 9. Configuration Nginx (Recommandé)

Créez un fichier de configuration Nginx `/etc/nginx/sites-available/keyper` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    
    # Redirection HTTPS (si vous avez SSL)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;
    
    # Certificats SSL (Let's Encrypt recommandé)
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    
    # Configuration SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Fichiers statiques
    location /static/ {
        alias /chemin/vers/KeyPer/staticfiles/;
    }
    
    # Fichiers médias
    location /media/ {
        alias /chemin/vers/KeyPer/media/;
    }
    
    # Application Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activer la configuration :

```bash
sudo ln -s /etc/nginx/sites-available/keyper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 10. Configuration systemd (Service Gunicorn)

Créez `/etc/systemd/system/keyper.service` :

```ini
[Unit]
Description=KeyPer Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/KeyPer
Environment="DJANGO_SETTINGS_MODULE=gestion_taches_project.settings_production"
ExecStart=/chemin/vers/KeyPer/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/keyper.sock \
    gestion_taches_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Démarrer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl start keyper
sudo systemctl enable keyper
```

### 11. Configuration SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique
sudo certbot renew --dry-run
```

### 12. Vérifications finales

```bash
# Vérifier que le service fonctionne
sudo systemctl status keyper

# Vérifier les logs
sudo journalctl -u keyper -f

# Tester l'application
curl https://votre-domaine.com
```

## 🔒 Sécurité

- ✅ Ne jamais commiter `.env` ou `settings_production.py` avec des valeurs réelles
- ✅ Utiliser HTTPS en production
- ✅ Configurer un firewall (UFW recommandé)
- ✅ Mettre à jour régulièrement les dépendances
- ✅ Utiliser des mots de passe forts pour la base de données
- ✅ Configurer des sauvegardes régulières

## 📦 Sauvegardes

```bash
# Sauvegarde de la base de données PostgreSQL
pg_dump -U keyper_user keyper_db > backup_$(date +%Y%m%d).sql

# Sauvegarde des fichiers médias
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## 🔄 Mises à jour

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour le code
git pull

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Appliquer les migrations
python manage.py migrate

# Recollecter les fichiers statiques
python manage.py collectstatic --noinput

# Redémarrer le service
sudo systemctl restart keyper
```

## 🐛 Dépannage

### Erreur 502 Bad Gateway
- Vérifier que Gunicorn fonctionne : `sudo systemctl status keyper`
- Vérifier les logs : `sudo journalctl -u keyper -n 50`

### Erreur 500 Internal Server Error
- Vérifier les logs Django : `tail -f logs/django.log`
- Vérifier les permissions des fichiers
- Vérifier la configuration de la base de données

### Fichiers statiques non chargés
- Vérifier que `collectstatic` a été exécuté
- Vérifier les permissions du dossier `staticfiles`
- Vérifier la configuration Nginx pour `/static/`

## 📞 Support

Pour toute question ou problème, consultez la documentation Django :
https://docs.djangoproject.com/en/stable/howto/deployment/

