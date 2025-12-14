# 📧 Guide de Configuration Email - KeyPer

Ce guide explique comment configurer l'envoi automatique d'emails pour les invitations dans KeyPer.

## 🎯 Fonctionnalités

Le système d'envoi d'emails permet d'envoyer automatiquement les codes d'invitation par email aux utilisateurs invités.

## ⚙️ Configuration

### Mode Développement (Par défaut)

En développement, les emails sont affichés dans la console du serveur Django. Aucune configuration supplémentaire n'est nécessaire.

Les emails apparaîtront dans votre terminal lorsque vous exécutez `python manage.py runserver`.

### Mode Production (SMTP)

Pour envoyer de vrais emails en production, vous devez configurer un serveur SMTP.

#### 1. Configuration Gmail

1. Ouvrez `gestion_taches_project/settings.py`
2. Décommentez et modifiez les lignes suivantes :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'  # Utilisez un mot de passe d'application
DEFAULT_FROM_EMAIL = 'KeyPer <votre-email@gmail.com>'
SERVER_EMAIL = 'KeyPer <votre-email@gmail.com>'
```

**Important pour Gmail :**
- Vous devez utiliser un **mot de passe d'application** (pas votre mot de passe Gmail normal)
- Pour créer un mot de passe d'application :
  1. Allez dans votre compte Google
  2. Sécurité → Validation en 2 étapes (doit être activée)
  3. Mots de passe des applications → Créer un nouveau mot de passe
  4. Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

#### 2. Configuration Autres Services SMTP

**Outlook/Office 365 :**
```python
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

**SendGrid :**
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'votre-clé-api-sendgrid'
```

**Mailgun :**
```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## 📝 Utilisation

### Créer une invitation avec envoi d'email

1. Allez sur la page de génération d'invitation pour un foyer
2. Remplissez le formulaire :
   - **Nom de l'invitation** (optionnel)
   - **Rôle** pour le nouvel utilisateur
   - **Cochez "Envoyer automatiquement l'invitation par email"**
   - **Entrez l'email du destinataire**
3. Cliquez sur "Générer l'Invitation"
4. L'invitation est créée et l'email est envoyé automatiquement

### Contenu de l'email

L'email envoyé contient :
- Un message personnalisé avec le nom de l'administrateur
- Le nom du foyer
- Le code d'invitation
- Un lien direct pour rejoindre le foyer
- Les instructions d'utilisation
- La date d'expiration (7 jours)

## 🔒 Sécurité

- Les emails sont envoyés de manière sécurisée via TLS/SSL
- Les codes d'invitation expirent après 7 jours
- Chaque code ne peut être utilisé qu'une seule fois
- Les mots de passe d'application doivent être stockés de manière sécurisée (variables d'environnement recommandées)

## 🛠️ Variables d'Environnement (Recommandé)

Pour plus de sécurité, utilisez des variables d'environnement au lieu de mettre les credentials directement dans `settings.py` :

1. Créez un fichier `.env` à la racine du projet :
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=KeyPer <noreply@keyper.com>
```

2. Installez `python-decouple` :
```bash
pip install python-decouple
```

3. Modifiez `settings.py` :
```python
from decouple import config

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='KeyPer <noreply@keyper.com>')
```

## 🐛 Dépannage

### Les emails ne sont pas envoyés

1. **Vérifiez la configuration SMTP** dans `settings.py`
2. **Vérifiez les logs** du serveur Django pour les erreurs
3. **Testez la connexion SMTP** avec un script de test
4. **Vérifiez les paramètres de sécurité** de votre compte email (autoriser les applications moins sécurisées si nécessaire)

### Erreur "Authentication failed"

- Vérifiez que vous utilisez un **mot de passe d'application** (pas votre mot de passe normal)
- Vérifiez que la validation en 2 étapes est activée (requis pour Gmail)
- Vérifiez que `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD` sont corrects

### Erreur "Connection refused"

- Vérifiez que le port SMTP est correct (587 pour TLS, 465 pour SSL)
- Vérifiez votre pare-feu
- Vérifiez que le serveur SMTP est accessible

## 📚 Ressources

- [Documentation Django Email](https://docs.djangoproject.com/en/stable/topics/email/)
- [Gmail - Mots de passe des applications](https://support.google.com/accounts/answer/185833)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Mailgun Documentation](https://documentation.mailgun.com/)

