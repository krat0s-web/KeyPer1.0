# 🚀 Déploiement RAPIDE - KeyPer sur Render.com

## ⚡ 5 ÉTAPES POUR METTRE EN LIGNE EN 10 MINUTES

### 1️⃣ **Créer un compte GitHub** (5 min)
```
https://github.com/signup
→ Vérifier votre email
```

### 2️⃣ **Créer un repository GitHub** (2 min)
```
https://github.com/new
- Name: keyper
- Visibility: Public ✅
Create Repository
```

### 3️⃣ **Pousser votre code** (1 min)
```bash
cd /home/kratos/Téléchargements/KeyPer
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/keyper.git
git push -u origin main
```

### 4️⃣ **Créer un compte Render** (3 min)
```
https://render.com
→ Sign Up with GitHub ✅
```

### 5️⃣ **Déployer sur Render** (2 min)
```
1. New + → Web Service
2. Sélectionner repository: keyper
3. Remplir:
   - Name: keyper
   - Build Command: pip install -r requirements.txt && python manage.py migrate
   - Start Command: gunicorn gestion_taches_project.wsgi:application --bind 0.0.0.0:$PORT
4. Advanced → Ajouter variables:
   - SECRET_KEY: [générer avec la commande ci-dessous]
   - DEBUG: False
   - ALLOWED_HOSTS: *.render.com
5. Create Web Service
6. Attendre 2-3 minutes...
7. 🟢 Live !
```

### 🔐 Générer une SECRET_KEY sécurisée

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiez la clé générée et collez-la dans Render.

---

## ✅ C'est tout !

Votre URL sera : **https://keyper.onrender.com** (à adapter avec votre nom)

Consultez `GUIDE_HEBERGEMENT_GRATUIT.md` pour les détails complets !
