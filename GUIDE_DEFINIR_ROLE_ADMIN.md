# 🔧 Guide : Définir le Rôle Admin pour un Utilisateur

Si vous êtes connecté avec un compte superuser Django mais que votre profil affiche "Membre" au lieu de "Administrateur", voici comment corriger :

---

## ✅ Solution Rapide

### **Méthode 1 : Via l'Admin Django** (Recommandé)

1. **Connectez-vous à l'admin Django** : `http://127.0.0.1:8000/admin/`
2. Allez dans **"MAISON_APP"** → **"Utilisateurs"**
3. **Trouvez votre utilisateur** (recherchez par email)
4. **Cliquez sur votre utilisateur** pour le modifier
5. Faites défiler jusqu'à la section **"Informations KeyPer"**
6. Dans le champ **"Rôle"**, sélectionnez **"Administrateur"**
7. Cliquez sur **"ENREGISTRER"**
8. **Déconnectez-vous et reconnectez-vous** à l'application pour que les changements prennent effet

### **Méthode 2 : Via le Shell Django**

```bash
python manage.py shell
```

Puis dans le shell :

```python
from maison_app.models import Utilisateur

# Trouver votre utilisateur
user = Utilisateur.objects.get(email='votre_email@exemple.com')

# Définir le rôle admin
user.role = 'admin'
user.save()

# Vérifier
print(f"Rôle : {user.get_role_display()}")
```

---

## 🔍 Vérification

Après avoir défini le rôle :

1. **Déconnectez-vous** de l'application
2. **Reconnectez-vous**
3. Allez sur `/mon-profil/`
4. Vous devriez voir :
   - **Rôle : Administrateur** (avec badge rouge)
   - **Bouton "Créer un foyer"** au lieu de "Rejoindre un foyer"
   - Vos foyers existants affichés avec photos

---

## ⚠️ Note Importante

- **Superuser Django** (`is_staff=True`) ≠ **Rôle Admin** dans l'application
- Pour utiliser toutes les fonctionnalités admin dans l'application, vous devez avoir **les deux** :
  - `is_staff=True` (pour accéder à l'admin Django)
  - `role='admin'` (pour les fonctionnalités admin dans l'application)

---

**C'est tout ! 🚀**

