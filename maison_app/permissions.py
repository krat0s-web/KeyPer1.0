"""
Système de permissions pour les rôles dans KeyPer
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


# === DÉFINITION DES PERMISSIONS PAR RÔLE ===

PERMISSIONS = {
    'admin': {
        'can_create_foyer': True,
        'can_edit_foyer': True,
        'can_delete_foyer': True,
        'can_add_piece': True,
        'can_delete_piece': True,
        'can_add_animal': True,
        'can_delete_animal': True,
        'can_restrict_piece_access': True,  # Peut restreindre l'accès aux pièces
        'can_create_tache': True,
        'can_edit_tache': True,
        'can_delete_tache': True,
        'can_assign_tache': True,
        'can_terminer_tache': True,
        'can_reactivate_own_tache': True,
        'can_access_calendrier': True,
        'can_add_evenement': True,
        'can_access_historique_taches': True,
        'can_manage_members': True,
        'can_generate_invitation': True,
        'can_delete_member': True,
        'can_access_budget': True,
        'can_create_depense': True,
        'can_delete_depense': True,
        'can_create_budget': True,
        'can_manage_demandes': True,  # Peut traiter les demandes
        'can_access_chat': True,
        'can_access_dashboard': True,
        'can_view_all_foyers': True,
        'can_modify_inventaire': True,
        'can_view_stock': True,
        'can_modify_stock': True,
        'can_create_liste_courses': True,
        'can_view_liste_courses': True,
        'can_modify_liste_courses': True,
        'can_view_menus': True,
        'can_modify_menus': True,
        'can_view_recettes': True,
        'can_generate_recettes': True,
        'can_view_historique_recettes': True,
        'can_add_note': True,
        'can_access_recompenses': True,
        'can_access_trophees': True,
        'can_manage_preferences': True,
        'can_view_stats': True,
        'can_access_demandes': True,
    },
    'tresorier': {
        'can_create_foyer': True,  # Peut créer son propre foyer
        'can_edit_foyer': False,
        'can_delete_foyer': False,
        'can_add_piece': False,
        'can_delete_piece': False,
        'can_add_animal': False,
        'can_delete_animal': False,
        'can_create_tache': False,
        'can_edit_tache': False,
        'can_delete_tache': False,
        'can_assign_tache': False,
        'can_terminer_tache': False,
        'can_manage_members': False,
        'can_generate_invitation': False,
        'can_delete_member': False,
        'can_access_budget': True,  # ✅ Accès uniquement à la trésorerie
        'can_create_depense': True,
        'can_delete_depense': True,
        'can_create_budget': True,
        'can_access_chat': True,
        'can_access_dashboard': False,
        'can_view_all_foyers': False,
        'can_view_stock': False,
        'can_modify_stock': False,
        'can_create_liste_courses': False,
        'can_view_liste_courses': False,
        'can_modify_liste_courses': False,
        'can_view_menus': False,
        'can_modify_menus': False,
        'can_view_recettes': False,
        'can_generate_recettes': False,
        'can_view_historique_recettes': False,
        'can_access_demandes': True,  # Peut voir les demandes
    },
    'membre': {
        'can_create_foyer': True,  # Peut créer son propre foyer
        'can_edit_foyer': False,  # Ne peut modifier que les foyers qu'il a créés
        'can_delete_foyer': False,
        'can_add_piece': False,
        'can_delete_piece': False,
        'can_add_animal': False,
        'can_delete_animal': False,
        'can_create_tache': True,
        'can_edit_tache': False,
        'can_delete_tache': False,
        'can_assign_tache': False,
        'can_terminer_tache': True,  # Peut terminer uniquement ses propres tâches
        'can_reactivate_own_tache': True,  # Peut réactiver uniquement ses propres tâches
        'can_access_calendrier': True,
        'can_add_evenement': True,
        'can_access_historique_taches': True,
        'can_manage_members': False,
        'can_generate_invitation': False,
        'can_delete_member': False,
        'can_access_budget': True,  # Accès en lecture seule, doit faire demande pour créer
        'can_create_depense': False,  # Doit faire une demande
        'can_delete_depense': False,
        'can_create_budget': False,  # Doit faire une demande
        'can_request_budget': True,  # Peut faire des demandes
        'can_access_chat': True,
        'can_access_dashboard': True,
        'can_view_all_foyers': False,
        'can_modify_inventaire': True,  # Accès complet cuisine
        'can_view_stock': True,
        'can_modify_stock': True,
        'can_create_liste_courses': True,
        'can_view_liste_courses': True,
        'can_modify_liste_courses': True,
        'can_view_menus': True,
        'can_modify_menus': True,
        'can_view_recettes': True,
        'can_generate_recettes': True,
        'can_view_historique_recettes': True,
        'can_add_note': True,
        'can_access_recompenses': True,
        'can_access_trophees': True,
        'can_manage_preferences': True,
        'can_view_stats': True,
        'can_access_demandes': True,  # Peut voir ses propres demandes
    },
    'junior': {
        'can_create_foyer': True,  # Peut créer son propre foyer
        'can_edit_foyer': False,  # Ne peut modifier que les foyers qu'il a créés
        'can_delete_foyer': False,
        'can_add_piece': False,
        'can_delete_piece': False,
        'can_add_animal': False,
        'can_delete_animal': False,
        'can_create_tache': True,
        'can_edit_tache': False,
        'can_delete_tache': False,
        'can_assign_tache': False,
        'can_terminer_tache': True,  # Peut terminer uniquement ses propres tâches
        'can_reactivate_own_tache': True,  # Peut réactiver uniquement ses propres tâches
        'can_access_calendrier': True,
        'can_add_evenement': True,
        'can_access_historique_taches': True,
        'can_manage_members': False,
        'can_generate_invitation': False,
        'can_delete_member': False,
        'can_access_budget': False,  # Pas d'accès au budget
        'can_create_depense': False,
        'can_delete_depense': False,
        'can_create_budget': False,
        'can_request_budget': False,
        'can_access_chat': True,
        'can_access_dashboard': True,
        'can_view_all_foyers': False,
        'can_modify_inventaire': False,  # Lecture seule pour cuisine
        'can_view_inventaire': True,
        'can_view_stock': True,
        'can_modify_stock': False,  # Lecture seule
        'can_create_liste_courses': False,
        'can_view_liste_courses': True,
        'can_modify_liste_courses': False,  # Lecture seule
        'can_view_menus': True,
        'can_modify_menus': False,  # Lecture seule
        'can_view_recettes': True,
        'can_generate_recettes': False,
        'can_view_historique_recettes': True,
        'can_add_note': True,
        'can_access_recompenses': True,
        'can_access_trophees': True,
        'can_manage_preferences': True,
        'can_view_stats': True,
        'can_access_demandes': True,  # Peut voir ses propres demandes
    },
    'invite': {
        'can_create_foyer': True,  # Peut créer son propre foyer
        'can_edit_foyer': False,
        'can_delete_foyer': False,
        'can_add_piece': False,
        'can_delete_piece': False,
        'can_add_animal': False,
        'can_delete_animal': False,
        'can_create_tache': False,
        'can_edit_tache': False,
        'can_delete_tache': False,
        'can_assign_tache': False,
        'can_terminer_tache': False,
        'can_manage_members': False,
        'can_generate_invitation': False,
        'can_delete_member': False,
        'can_access_budget': False,
        'can_create_depense': False,
        'can_delete_depense': False,
        'can_create_budget': False,
        'can_access_chat': True,  # Peut voir le chat
        'can_access_dashboard': False,
        'can_view_all_foyers': False,
        'can_modify_inventaire': False,
        'can_view_stock': False,
        'can_modify_stock': False,
        'can_create_liste_courses': False,
        'can_view_liste_courses': False,
        'can_modify_liste_courses': False,
        'can_view_menus': False,
        'can_modify_menus': False,
        'can_view_recettes': False,
        'can_generate_recettes': False,
        'can_view_historique_recettes': False,
        'can_add_note': False,
        'can_access_recompenses': False,
        'can_access_trophees': False,
        'can_manage_preferences': False,
        'can_view_stats': False,
        'can_access_demandes': True,  # Peut voir les demandes
    },
    'observateur': {
        'can_create_foyer': True,  # Peut créer son propre foyer
        'can_edit_foyer': False,  # Ne peut modifier que les foyers qu'il a créés
        'can_delete_foyer': False,
        'can_add_piece': False,
        'can_delete_piece': False,
        'can_add_animal': False,
        'can_delete_animal': False,
        'can_create_tache': False,
        'can_edit_tache': False,
        'can_delete_tache': False,
        'can_assign_tache': False,
        'can_terminer_tache': False,
        'can_reactivate_own_tache': False,
        'can_access_calendrier': True,  # Lecture seule
        'can_add_evenement': False,
        'can_access_historique_taches': True,  # Lecture seule
        'can_manage_members': False,
        'can_generate_invitation': False,
        'can_delete_member': False,
        'can_access_budget': False,  # Pas d'accès au budget
        'can_create_depense': False,
        'can_delete_depense': False,
        'can_create_budget': False,
        'can_request_budget': False,
        'can_access_chat': True,  # Lecture seule du chat
        'can_access_dashboard': True,  # Peut voir le dashboard en lecture seule
        'can_view_all_foyers': False,
        'can_modify_inventaire': False,  # Ne peut pas modifier le stock
        'can_view_inventaire': True,  # Peut voir le stock en lecture seule
        'can_view_stock': True,  # Peut voir le stock en lecture seule
        'can_modify_stock': False,  # Ne peut pas modifier le stock
        'can_create_liste_courses': False,  # Ne peut pas créer de listes de courses
        'can_view_liste_courses': True,  # Peut voir les listes en lecture seule
        'can_modify_liste_courses': False,  # Ne peut pas modifier les listes
        'can_view_menus': True,  # Peut voir les menus en lecture seule
        'can_modify_menus': False,  # Ne peut pas modifier les menus
        'can_view_recettes': True,  # Peut voir les recettes en lecture seule
        'can_generate_recettes': False,
        'can_view_historique_recettes': True,  # Peut voir l'historique des recettes
        'can_add_note': False,  # Ne peut pas ajouter de note
        'can_access_recompenses': False,  # Pas de récompenses
        'can_access_trophees': False,  # Pas de trophées
        'can_manage_preferences': True,  # Peut gérer ses préférences
        'can_view_stats': True,  # Peut voir ses stats
        'can_access_demandes': True,  # Peut voir les demandes (lecture seule)
    },
}


def has_permission(user, permission, foyer=None):
    """
    Vérifie si un utilisateur a une permission donnée
    Si foyer est fourni, vérifie aussi les permissions personnalisées pour ce foyer
    Si foyer n'est pas fourni mais que l'utilisateur a un foyer_actif, l'utilise
    """
    if not user.is_authenticated:
        return False
    
    # Les superusers Django ont tous les droits
    if user.is_staff and user.is_superuser:
        return True
    
    # Si aucun foyer n'est fourni, essayer d'utiliser le foyer actif de l'utilisateur
    if foyer is None and hasattr(user, 'foyer_actif') and user.foyer_actif:
        foyer = user.foyer_actif
    
    # Vérifier les permissions personnalisées par foyer si un foyer est disponible
    if foyer and hasattr(user, 'permissions_foyer'):
        try:
            from .models import PermissionFoyer
            perm_foyer = PermissionFoyer.objects.get(id_user=user, id_foyer=foyer)
            
            # Permissions budget - si l'utilisateur a une permission personnalisée, l'utiliser
            if permission == 'can_access_budget':
                return perm_foyer.can_access_budget
            elif permission == 'can_create_depense':
                return perm_foyer.can_create_depense
            elif permission == 'can_delete_depense':
                return perm_foyer.can_delete_depense
            elif permission == 'can_create_budget':
                return perm_foyer.can_create_budget
        except PermissionFoyer.DoesNotExist:
            pass
        except Exception:
            pass
    
    # Récupérer les permissions du rôle
    role = user.role if hasattr(user, 'role') else 'membre'
    role_permissions = PERMISSIONS.get(role, PERMISSIONS['membre'])
    
    return role_permissions.get(permission, False)


def require_permission(permission, redirect_url='liste_foyers', error_message=None):
    """
    Décorateur pour vérifier une permission avant d'accéder à une vue
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_permission(request.user, permission):
                if error_message:
                    messages.error(request, error_message)
                else:
                    messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(*allowed_roles, redirect_url='liste_foyers', error_message=None):
    """
    Décorateur pour vérifier que l'utilisateur a un rôle spécifique
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.user.role if hasattr(request.user, 'role') else 'membre'
            
            # Les superusers Django sont considérés comme admin
            if request.user.is_staff and request.user.is_superuser:
                user_role = 'admin'
            
            if user_role not in allowed_roles:
                if error_message:
                    messages.error(request, error_message)
                else:
                    messages.error(request, "Accès refusé. Rôle requis : " + ", ".join(allowed_roles))
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

