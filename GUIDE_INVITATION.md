# 📋 Guide : Générer un Code d'Invitation pour un Foyer

Ce guide vous explique comment, en tant qu'**administrateur**, générer un code d'invitation pour permettre à d'autres personnes de rejoindre votre foyer.

---

## ⚠️ Important : Foyer Créé dans l'Admin Django ?

Si vous avez créé un foyer dans l'espace admin Django (`/admin/`), **il n'est pas automatiquement associé à votre compte**. 

👉 **Consultez d'abord** : `GUIDE_ASSOCIER_FOYER_ADMIN.md` pour associer le foyer à votre compte.

---

## 🎯 Prérequis

- ✅ Avoir un compte avec le rôle **"admin"** dans l'application
- ✅ Être connecté à l'application
- ✅ Avoir au moins un foyer créé **ET associé à votre compte** (visible dans `/foyers/`)

---

## 📝 Étapes Détaillées

### **Étape 1 : Se connecter en tant qu'admin**

1. **Lancez le serveur Django** (si ce n'est pas déjà fait) :
   ```bash
   python manage.py runserver
   ```

2. **Ouvrez votre navigateur** et allez à :
   ```
   http://127.0.0.1:8000/
   ```

3. **Connectez-vous** avec vos identifiants admin :
   - Si vous n'avez pas encore de compte admin, créez-en un d'abord (voir section "Créer un compte admin" ci-dessous)

---

### **Étape 2 : Vérifier ou créer un foyer**

#### **Option A : Si vous avez déjà un foyer**

1. Cliquez sur l'icône **"Foyer"** dans le menu de navigation (ou allez à `/foyers/`)
2. Vous verrez la liste de vos foyers
3. Passez à l'**Étape 3**

#### **Option B : Si vous devez créer un foyer**

1. Cliquez sur l'icône **"Foyer"** dans le menu de navigation
2. Cliquez sur le bouton **"+ Créer un foyer"** (visible uniquement si vous êtes admin)
3. Remplissez le formulaire :
   - **Nom du foyer** : ex. "Maison Dupont"
   - **Description** : (optionnel) Description de votre foyer
   - **Photo** : (optionnel) Téléchargez une photo
4. Cliquez sur **"Créer le foyer"**
5. Vous serez redirigé vers la liste des foyers

---

### **Étape 3 : Accéder à la page de génération d'invitation**

Il y a **deux façons** d'accéder à la page de génération d'invitation :

#### **Méthode 1 : Depuis la page de détail du foyer** (Recommandé)

1. Sur la page **"Mes Foyers"** (`/foyers/`), cliquez sur la **carte du foyer** pour lequel vous voulez générer un code
2. Vous arrivez sur la page de détail du foyer (`/foyer/<id>/`)
3. Faites défiler jusqu'à la section **"Inviter membre"**
4. Cliquez sur le bouton **"+ Inviter un membre"**

#### **Méthode 2 : Via l'URL directe**

1. Notez l'**ID du foyer** (visible dans l'URL quand vous êtes sur la page de détail)
2. Allez directement à :
   ```
   http://127.0.0.1:8000/foyer/<ID_FOYER>/inviter/
   ```
   Remplacez `<ID_FOYER>` par l'ID réel (ex. : `http://127.0.0.1:8000/foyer/1/inviter/`)

---

### **Étape 4 : Générer le code d'invitation**

1. Sur la page **"Générer Invitation"**, vous verrez :
   - Si un code existe déjà : le code actuel avec ses informations
   - Un formulaire pour générer ou régénérer un code

2. **Choisissez le rôle** pour le nouvel utilisateur :
   - **Membre** : Accès standard
   - **Trésorier** : Gestion des finances
   - **Junior** : Accès limité
   - **Invité** : Accès très limité
   - **Observateur** : Accès en lecture seule

3. Cliquez sur **"✅ Générer le Code"** (ou **"🔄 Régénérer le Code"** si un code existe déjà)

4. **Le code s'affiche** immédiatement dans une boîte bleue en haut de la page

5. **Copiez le code** :
   - Cliquez sur le bouton **"📋 Copier"** à côté du code
   - Ou sélectionnez manuellement le code et copiez-le (Ctrl+C)

   Le code ressemble à : `b9e61bff-d34f-4d90-9236-fca9e61b9e61`

---

### **Étape 5 : Partager le code**

Envoyez le code à la personne que vous souhaitez inviter :
- Par email
- Par message
- Par tout autre moyen de communication

**⚠️ Important :**
- Le code est **valide pendant 7 jours** après sa création
- Le code ne peut être utilisé **qu'une seule fois**
- Si le code est utilisé, vous devrez en générer un nouveau

---

## 🧪 Tester le Code d'Invitation

### **Test 1 : Rejoindre avec un utilisateur non connecté**

1. **Ouvrez une fenêtre de navigation privée** (ou un autre navigateur) pour simuler un nouvel utilisateur
2. Allez à :
   ```
   http://127.0.0.1:8000/rejoindre/
   ```
3. Remplissez le formulaire :
   - **Code d'invitation** : Collez le code que vous avez généré
   - **Votre nom** : Ex. "Jean Dupont"
   - **Votre email** : Ex. "jean@exemple.com"
4. Cliquez sur **"Rejoindre"**
5. ✅ L'utilisateur sera automatiquement créé, connecté et ajouté au foyer

### **Test 2 : Rejoindre avec un utilisateur déjà connecté**

1. **Connectez-vous** avec un autre compte (ou créez-en un via `/inscription/`)
2. Allez à :
   ```
   http://127.0.0.1:8000/rejoindre/
   ```
3. Entrez le **code d'invitation**
4. Cliquez sur **"Rejoindre"**
5. ✅ L'utilisateur sera ajouté au foyer avec le rôle spécifié

---

## 🔍 Vérifier que ça fonctionne

Après qu'un utilisateur a rejoint avec le code :

1. **En tant qu'admin**, allez sur la page de détail du foyer
2. Faites défiler jusqu'à la section **"Membres"**
3. Vous devriez voir le nouvel utilisateur dans la liste
4. Le code d'invitation utilisé ne sera plus valide (marqué comme "utilisé")

---

## 🛠️ Dépannage

### **Problème : "Accès refusé. Seuls les administrateurs peuvent inviter."**

**Solution :** Votre compte n'a pas le rôle "admin". Vérifiez votre rôle dans votre profil ou contactez un superutilisateur.

### **Problème : "Code invalide"**

**Solutions possibles :**
- Le code a déjà été utilisé (générez-en un nouveau)
- Le code a expiré (valide 7 jours, générez-en un nouveau)
- Le code a été mal copié (vérifiez qu'il n'y a pas d'espaces)

### **Problème : "Cet email est déjà utilisé"**

**Solution :** L'email existe déjà dans le système. L'utilisateur doit se connecter avec son compte existant, puis utiliser le code.

### **Problème : Le bouton "Inviter un membre" n'apparaît pas**

**Solutions :**
- Vérifiez que vous êtes bien connecté avec un compte admin
- Vérifiez que vous êtes sur la page de détail du foyer (pas sur la liste)
- Rafraîchissez la page (F5)

---

## 📌 Récapitulatif Rapide

```
1. Se connecter en tant qu'admin
2. Aller sur /foyers/
3. Cliquer sur un foyer
4. Cliquer sur "+ Inviter un membre"
5. Choisir un rôle
6. Cliquer sur "Générer le Code"
7. Copier le code
8. Partager le code
9. L'invité va sur /rejoindre/ et entre le code
```

---

## 💡 Astuces

- **Générer plusieurs codes** : Vous pouvez générer plusieurs codes pour le même foyer, mais chaque code ne peut être utilisé qu'une fois
- **Régénérer un code** : Si un code est expiré ou utilisé, cliquez sur "Régénérer le Code"
- **Rôles différents** : Vous pouvez générer des codes avec des rôles différents pour donner des permissions différentes
- **Voir les codes actifs** : Sur la page de génération, vous voyez toujours le code actuel (non utilisé) s'il existe

---

## 🎓 Créer un Compte Admin (si nécessaire)

Si vous n'avez pas encore de compte admin :

1. **Créez un superutilisateur Django** :
   ```bash
   python manage.py createsuperuser
   ```
   Suivez les instructions pour créer le compte.

2. **Connectez-vous** avec ce compte sur `/accounts/login/`

3. **Modifiez le rôle** :
   - Allez sur `/mon-profil/`
   - Changez votre rôle en "Administrateur"
   - OU utilisez l'admin Django (`/admin/`) pour modifier le rôle

---

**Bon test ! 🚀**

