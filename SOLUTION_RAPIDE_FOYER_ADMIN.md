# ⚡ Solution Rapide : Foyer Créé dans l'Admin

## 🎯 Votre Problème

Vous avez créé un foyer dans l'admin Django (`/admin/`), mais :
- ❌ Vous ne le voyez pas dans `/foyers/`
- ❌ Vous ne pouvez pas générer de code d'invitation

## ✅ Solution en 3 Étapes (2 minutes)

### **Étape 1 : Associer le foyer à votre compte**

1. Allez sur : `http://127.0.0.1:8000/admin/maison_app/utilisateur/`
2. Cliquez sur **votre utilisateur** (recherchez par email)
3. Faites défiler jusqu'à **"Informations KeyPer"**
4. Dans **"Foyers"** :
   - Sélectionnez votre foyer dans la liste de gauche
   - Cliquez sur la **flèche droite (→)** pour l'ajouter
5. Dans **"Foyer actif"**, sélectionnez ce foyer
6. Cliquez sur **"ENREGISTRER"**

### **Étape 2 : Vérifier**

1. Allez sur : `http://127.0.0.1:8000/foyers/`
2. ✅ Vous devriez voir votre foyer !

### **Étape 3 : Générer un code d'invitation**

**Option A : Depuis l'application** (Recommandé)
1. Cliquez sur votre foyer
2. Cliquez sur **"+ Inviter un membre"**
3. Choisissez un rôle et générez le code

**Option B : Depuis l'admin**
1. Allez sur : `http://127.0.0.1:8000/admin/maison_app/invitation/add/`
2. Sélectionnez votre foyer, un rôle, et votre utilisateur
3. Enregistrez → Le code s'affiche

---

## 📚 Guides Complets

- **Guide détaillé** : `GUIDE_ASSOCIER_FOYER_ADMIN.md`
- **Guide invitations** : `GUIDE_INVITATION.md`

---

## 💡 Pour Éviter ce Problème à l'Avenir

Créez vos foyers directement depuis l'application :
1. Allez sur `/foyers/`
2. Cliquez sur **"+ Créer un foyer"**
3. Le foyer sera automatiquement associé à votre compte ! ✅

---

**C'est tout ! 🚀**



