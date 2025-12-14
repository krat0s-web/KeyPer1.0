# 🔗 Guide : Associer un Foyer Créé dans l'Admin à Votre Compte

Si vous avez créé un foyer dans l'espace admin Django (`/admin/`), ce guide vous explique comment l'associer à votre compte utilisateur pour pouvoir le voir dans l'application et générer des codes d'invitation.

---

## 🎯 Problème

Quand vous créez un foyer dans l'admin Django, il n'est **pas automatiquement associé** à votre compte utilisateur. C'est pourquoi vous ne le voyez pas dans `/foyers/` ou `/mon-profil/`.

---

## ✅ Solution : Deux Méthodes

### **Méthode 1 : Via l'Admin Django** (Recommandé)

#### **Étape 1 : Trouver votre utilisateur dans l'admin**

1. Allez sur l'admin Django : `http://127.0.0.1:8000/admin/`
2. Dans la section **"MAISON_APP"**, cliquez sur **"Utilisateurs"**
3. Trouvez votre utilisateur (recherchez par email ou nom)
4. Cliquez sur votre utilisateur pour le modifier

#### **Étape 2 : Associer le foyer à votre compte**

1. Faites défiler jusqu'à la section **"Informations KeyPer"**
2. Dans le champ **"Foyers"**, vous verrez deux listes :
   - **Liste de gauche** : Foyers disponibles
   - **Liste de droite** : Foyers associés à votre compte

3. **Sélectionnez le foyer** que vous avez créé dans la liste de gauche
4. Cliquez sur la **flèche vers la droite (→)** pour l'ajouter à votre compte
5. **Optionnel** : Dans le champ **"Foyer actif"**, sélectionnez ce foyer (pour qu'il soit votre foyer par défaut)
6. Cliquez sur **"ENREGISTRER"** en bas de la page

#### **Étape 3 : Vérifier**

1. Allez sur l'application : `http://127.0.0.1:8000/foyers/`
2. Vous devriez maintenant voir votre foyer ! ✅

---

### **Méthode 2 : Via l'Interface Utilisateur** (Si vous avez déjà un foyer)

Si vous avez déjà un autre foyer associé à votre compte, vous pouvez utiliser un code d'invitation :

1. Créez un code d'invitation pour le foyer (voir section suivante)
2. Utilisez ce code sur `/rejoindre/` avec votre compte
3. Le foyer sera ajouté à votre compte

---

## 🔑 Générer un Code d'Invitation depuis l'Admin

Maintenant que votre foyer est associé à votre compte, vous pouvez générer un code d'invitation de **deux façons** :

### **Option A : Depuis l'Admin Django** (Nouveau !)

1. Allez sur l'admin : `http://127.0.0.1:8000/admin/`
2. Dans **"MAISON_APP"**, cliquez sur **"Foyers"**
3. Cliquez sur le foyer pour lequel vous voulez générer un code
4. En haut de la page, vous verrez un lien **"Générer un code"** dans la colonne "Action"
5. OU allez dans **"Invitations"** et cliquez sur **"+ Ajouter"**
6. Remplissez le formulaire :
   - **Foyer** : Sélectionnez votre foyer
   - **Rôle** : Choisissez le rôle (Membre, Trésorier, etc.)
   - **Créé par** : Sélectionnez votre utilisateur
7. Cliquez sur **"ENREGISTRER"**
8. Le code s'affichera dans la liste des invitations

### **Option B : Depuis l'Interface Utilisateur** (Recommandé)

1. Allez sur l'application : `http://127.0.0.1:8000/foyers/`
2. Cliquez sur votre foyer
3. Cliquez sur **"+ Inviter un membre"**
4. Choisissez un rôle et générez le code
5. Copiez le code et partagez-le

---

## 📋 Récapitulatif Rapide

```
1. Admin → Utilisateurs → Votre compte
2. Section "Informations KeyPer" → Champ "Foyers"
3. Sélectionnez le foyer → Flèche droite (→)
4. Optionnel : Définir "Foyer actif"
5. Enregistrer
6. Vérifier sur /foyers/
```

---

## 🛠️ Dépannage

### **Problème : Je ne vois pas le champ "Foyers" dans l'admin**

**Solution :** Vérifiez que vous êtes bien connecté en tant que superutilisateur (pas juste un utilisateur avec le rôle "admin" dans l'application).

### **Problème : Le foyer n'apparaît toujours pas dans /foyers/**

**Solutions :**
1. Vérifiez que vous avez bien enregistré les modifications dans l'admin
2. Déconnectez-vous et reconnectez-vous à l'application
3. Vérifiez que votre compte a bien le rôle "admin" dans l'application (pas seulement dans Django admin)

### **Problème : Je ne peux pas générer de code d'invitation**

**Solutions :**
1. Vérifiez que votre compte a le rôle "admin" dans l'application (`/mon-profil/`)
2. Vérifiez que le foyer est bien associé à votre compte
3. Utilisez l'interface utilisateur (`/foyers/`) plutôt que l'admin pour générer le code

---

## 💡 Astuce : Créer un Foyer Directement depuis l'Application

Pour éviter ce problème à l'avenir, créez vos foyers directement depuis l'application :

1. Connectez-vous à l'application : `http://127.0.0.1:8000/`
2. Allez sur `/foyers/`
3. Cliquez sur **"+ Créer un foyer"**
4. Le foyer sera automatiquement associé à votre compte ! ✅

---

## 🎓 Vérifier Votre Rôle Admin

Pour générer des codes d'invitation depuis l'interface utilisateur, votre compte doit avoir le rôle **"admin"** :

1. Allez sur : `http://127.0.0.1:8000/mon-profil/`
2. Vérifiez votre rôle
3. Si ce n'est pas "admin", modifiez-le :
   - Via l'admin Django : `/admin/maison_app/utilisateur/<votre_id>/change/`
   - Ou modifiez directement dans votre profil si vous avez les permissions

---

**Maintenant vous pouvez gérer vos foyers et inviter des membres ! 🚀**

