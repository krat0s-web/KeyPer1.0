# 🔐 Guide : Système de Permissions et Rôles

Ce document décrit le système de permissions par rôle implémenté dans KeyPer.

---

## 📋 Rôles Disponibles

1. **Administrateur** (`admin`) : Accès complet
2. **Trésorier** (`tresorier`) : Accès uniquement à la trésorerie
3. **Membre** (`membre`) : Accès standard
4. **Junior** (`junior`) : Accès limité
5. **Invité** (`invite`) : Accès très limité
6. **Observateur** (`observateur`) : Accès en lecture seule

---

## 🔑 Permissions par Rôle

### **👑 Administrateur**

**Accès complet à toutes les fonctionnalités :**
- ✅ Créer, modifier, supprimer des foyers
- ✅ Ajouter, supprimer des pièces et animaux
- ✅ Créer, modifier, supprimer des tâches
- ✅ Assigner des tâches
- ✅ Gérer les membres (inviter, supprimer)
- ✅ Accéder à la trésorerie (budget et dépenses)
- ✅ Accéder au chat
- ✅ Accéder au dashboard
- ✅ Voir tous les foyers

---

### **💰 Trésorier**

**Accès uniquement à la trésorerie :**
- ❌ Ne peut pas créer/modifier/supprimer des foyers
- ❌ Ne peut pas ajouter/supprimer des pièces et animaux
- ❌ Ne peut pas créer/modifier/supprimer des tâches
- ❌ Ne peut pas gérer les membres
- ✅ **Peut accéder à la trésorerie** (budget et dépenses)
- ✅ **Peut créer des dépenses**
- ✅ **Peut supprimer des dépenses**
- ✅ **Peut créer des budgets**
- ✅ Peut accéder au chat
- ❌ Ne peut pas accéder au dashboard
- ❌ Ne peut pas voir tous les foyers

---

### **👤 Membre**

**Accès standard :**
- ❌ Ne peut pas créer/modifier/supprimer des foyers
- ❌ Ne peut pas ajouter/supprimer des pièces et animaux
- ✅ Peut créer des tâches
- ❌ Ne peut pas modifier/supprimer des tâches
- ✅ Peut terminer des tâches
- ❌ Ne peut pas gérer les membres
- ❌ Ne peut pas accéder à la trésorerie
- ✅ Peut accéder au chat
- ✅ Peut accéder au dashboard

---

### **🧒 Junior**

**Accès limité :**
- ❌ Ne peut pas créer/modifier/supprimer des foyers
- ❌ Ne peut pas ajouter/supprimer des pièces et animaux
- ❌ Ne peut pas créer des tâches
- ✅ Peut terminer des tâches (assignées)
- ❌ Ne peut pas gérer les membres
- ❌ Ne peut pas accéder à la trésorerie
- ✅ Peut accéder au chat
- ✅ Peut accéder au dashboard

---

### **👋 Invité**

**Accès très limité :**
- ❌ Ne peut pas créer/modifier/supprimer des foyers
- ❌ Ne peut pas ajouter/supprimer des pièces et animaux
- ❌ Ne peut pas créer/modifier/supprimer des tâches
- ❌ Ne peut pas terminer des tâches
- ❌ Ne peut pas gérer les membres
- ❌ Ne peut pas accéder à la trésorerie
- ✅ Peut accéder au chat (lecture seule)
- ❌ Ne peut pas accéder au dashboard

---

### **👁️ Observateur**

**Accès en lecture seule :**
- ❌ Ne peut pas créer/modifier/supprimer des foyers
- ❌ Ne peut pas ajouter/supprimer des pièces et animaux
- ❌ Ne peut pas créer/modifier/supprimer des tâches
- ❌ Ne peut pas terminer des tâches
- ❌ Ne peut pas gérer les membres
- ❌ Ne peut pas accéder à la trésorerie
- ✅ Peut accéder au chat (lecture seule)
- ✅ Peut accéder au dashboard (lecture seule)

---

## 🏠 Modification des Foyers

**Seuls les administrateurs peuvent modifier un foyer :**
- ✅ Modifier le nom
- ✅ Modifier la description
- ✅ Modifier/Supprimer la photo
- ✅ Accès via : Page de détail du foyer → Bouton "Modifier"

---

## 💡 Utilisation dans le Code

### **Vérifier une permission :**

```python
from maison_app.permissions import has_permission

if has_permission(request.user, 'can_access_budget'):
    # L'utilisateur peut accéder au budget
    pass
```

### **Décorateur pour une vue :**

```python
from maison_app.permissions import require_permission

@login_required
@require_permission('can_create_foyer', error_message="Seuls les administrateurs peuvent créer un foyer.")
def creer_foyer(request):
    # ...
```

### **Décorateur pour un rôle spécifique :**

```python
from maison_app.permissions import require_role

@login_required
@require_role('admin', 'tresorier', error_message="Accès réservé aux administrateurs et trésoriers.")
def budget_foyer(request):
    # ...
```

---

## 📝 Liste Complète des Permissions

| Permission | Admin | Trésorier | Membre | Junior | Invité | Observateur |
|------------|-------|-----------|--------|--------|--------|-------------|
| `can_create_foyer` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_edit_foyer` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_foyer` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_add_piece` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_piece` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_add_animal` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_animal` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_create_tache` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `can_edit_tache` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_tache` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_assign_tache` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_terminer_tache` | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| `can_manage_members` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_generate_invitation` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_member` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `can_access_budget` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `can_create_depense` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `can_delete_depense` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `can_create_budget` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `can_access_chat` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `can_access_dashboard` | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `can_view_all_foyers` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 Cas d'Usage

### **Scénario 1 : Trésorier**
Un utilisateur avec le rôle "Trésorier" peut :
- ✅ Accéder à la page Budget
- ✅ Créer des dépenses
- ✅ Créer des budgets
- ✅ Supprimer des dépenses
- ❌ Ne peut pas créer/modifier des foyers
- ❌ Ne peut pas gérer les tâches
- ❌ Ne peut pas accéder au dashboard

### **Scénario 2 : Admin modifie un foyer**
Un administrateur peut :
- ✅ Aller sur la page de détail d'un foyer
- ✅ Cliquer sur "Modifier"
- ✅ Modifier le nom, la description, la photo
- ✅ Enregistrer les modifications

---

## 🔧 Configuration

Les permissions sont définies dans `maison_app/permissions.py` dans le dictionnaire `PERMISSIONS`.

Pour modifier les permissions d'un rôle, éditez ce fichier.

---

**Document créé le** : 2025  
**Dernière mise à jour** : Implémentation initiale

