# 🏠 KeyPer - Application de Gestion Familiale

KeyPer est une application web complète de gestion familiale permettant d'organiser les tâches, le budget, les notes, le chat et bien plus encore pour toute la famille.

## ✨ Fonctionnalités Principales

### 👥 Gestion de Foyer
- Création et gestion de plusieurs foyers
- Système d'invitation par code
- Rôles personnalisables (Admin, Membre, Junior, Observateur, etc.)

### ✅ Gestion des Tâches
- Création et assignation de tâches
- Calendrier des tâches et événements
- Historique et réactivation des tâches
- Système de points et récompenses

### 💰 Budget Familial
- Suivi des dépenses par catégorie
- Création de budgets
- Graphiques et statistiques
- Système de demandes pour les membres

### 💬 Communication
- Chat en temps réel par foyer
- Notifications pour les événements importants
- Commentaires sur les tâches

### 🍳 Gestion de Cuisine
- Gestion du stock alimentaire
- Listes de courses
- Menus de la semaine
- Génération de recettes avec API Forkify

### 📝 Notes et Organisation
- Notes colorées et personnalisables
- Organisation par catégories

### 🎮 Gamification
- Système de points et récompenses
- Trophées à débloquer
- Jeux (Snake, Puzzles)

### 🌤️ Météo
- Affichage de la météo par ville
- Recommandations vestimentaires
- Villes favorites

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL (recommandé) ou SQLite
- pip

### Installation locale

```bash
# Cloner le projet
git clone <votre-repo>
cd KeyPer

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

L'application sera accessible sur `http://127.0.0.1:8000`

## 📦 Dépendances Principales

- Django 5.2.7
- PostgreSQL (psycopg2-binary)
- Gunicorn (pour la production)
- Requests (pour les APIs externes)

Voir `requirements.txt` pour la liste complète.

## 🔧 Configuration

### Variables d'environnement

Copiez `.env.example` en `.env` et configurez :

```bash
SECRET_KEY=votre-clé-secrète
ALLOWED_HOSTS=votre-domaine.com
DB_NAME=keyper_db
DB_USER=keyper_user
DB_PASSWORD=votre-mot-de-passe
```

### Configuration de production

Voir `DEPLOYMENT.md` pour les instructions complètes de déploiement.

## 📁 Structure du Projet

```
KeyPer/
├── gestion_taches_project/    # Configuration Django
│   ├── settings.py           # Configuration développement
│   ├── settings_production.py # Configuration production
│   ├── urls.py               # Routes principales
│   └── wsgi.py               # Interface WSGI
├── maison_app/               # Application principale
│   ├── models.py             # Modèles de données
│   ├── views.py              # Vues et logique métier
│   ├── permissions.py        # Système de permissions RBAC
│   ├── forms.py              # Formulaires
│   ├── templates/            # Templates HTML
│   └── static/              # Fichiers statiques
├── static/                   # Fichiers statiques globaux
├── media/                   # Fichiers uploadés (photos, etc.)
├── requirements.txt         # Dépendances Python
├── DEPLOYMENT.md           # Guide de déploiement
└── README.md               # Ce fichier
```

## 🔐 Sécurité

- Authentification Django personnalisée
- Système de permissions basé sur les rôles (RBAC)
- Protection CSRF
- Validation des entrées utilisateur
- Gestion sécurisée des fichiers uploadés

## 🧪 Tests

```bash
# Lancer les tests
python manage.py test
```

## 📝 Licence

Ce projet est privé et propriétaire.

## 👨‍💻 Développement

### Ajouter une nouvelle fonctionnalité

1. Créer/modifier les modèles dans `maison_app/models.py`
2. Créer les migrations : `python manage.py makemigrations`
3. Appliquer les migrations : `python manage.py migrate`
4. Créer les vues dans `maison_app/views.py`
5. Créer les templates dans `maison_app/templates/`
6. Ajouter les routes dans `gestion_taches_project/urls.py`

### Code Style

- Suivre les conventions PEP 8
- Commenter le code complexe
- Utiliser des docstrings pour les fonctions importantes

## 🐛 Problèmes Connus

Aucun problème connu actuellement.

## 📞 Support

Pour toute question ou problème, consultez la documentation Django ou créez une issue.

## 🔄 Mises à Jour

Voir `DEPLOYMENT.md` pour les instructions de mise à jour en production.

---

**KeyPer** - Organisez votre foyer en toute simplicité 🏠✨
