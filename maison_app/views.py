"""
Vues principales de l'application KeyPer
=========================================

Ce module contient toutes les vues (fonctions) qui gèrent les requêtes HTTP
et rendent les templates correspondants.

Structure :
- Vues publiques (accueil, FAQ, login, inscription)
- Vues authentifiées (dashboard, tâches, foyers, profil, etc.)
- Vues API (endpoints JSON pour AJAX)
- Fonctions helper (trophées, permissions, etc.)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Tache, Foyer, Utilisateur, StatutTache, Invitation, Piece, Animal,
    ChatMessage, Note, Notification, Depense, Budget, CategorieDepense,
    TacheAssignee, Recompense, Trophee, Evenement, NiveauSnake,
    NiveauDebloque, HistoriqueTache, Demande, CommentaireTache
)
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm
from .models import ROLE_CHOICES
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q, Avg
from django.http import JsonResponse
from django.conf import settings
import os
import json

# === ACCUEIL ===
def accueil(request):
    """Page d'accueil"""
    return render(request, 'maison_app/accueil.html')

# === FAQ ===
def faq(request):
    """Page FAQ"""
    return render(request, 'maison_app/faq.html')

# === FONCTION HELPER POUR DÉBLOQUER AUTOMATIQUEMENT LES TROPHÉES ===
def verifier_et_debloquer_trophees(utilisateur, type_verification, request=None):
    """Fonction helper pour vérifier et débloquer automatiquement les trophées"""
    foyer = utilisateur.foyer_actif
    if not foyer:
        return None
    
    trophee_created = None
    
    if type_verification == 'budget':
        # Trophée Budget - 10 budgets créés
        nb_budgets = Budget.objects.filter(id_foyer=foyer).count()
        if nb_budgets >= 10:
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='budget',
                defaults={
                    'nom': '💰 Gestionnaire de Budget',
                    'description': 'Vous avez créé 10 budgets',
                    'icone': 'bi-wallet2',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Gestionnaire de Budget !")
    
    elif type_verification == 'animal':
        # Trophée Animal - 5 animaux ajoutés
        nb_animaux = Animal.objects.filter(id_foyer=foyer).count()
        if nb_animaux >= 5:
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='animal',
                defaults={
                    'nom': '🐾 Ami des Animaux',
                    'description': 'Vous avez ajouté 5 animaux',
                    'icone': 'bi-heart',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Ami des Animaux !")
    
    elif type_verification == 'note':
        # Trophée Note - 20 notes créées
        nb_notes = Note.objects.filter(id_user=utilisateur).count()
        if nb_notes >= 20:
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='note',
                defaults={
                    'nom': '📝 Preneur de Notes',
                    'description': 'Vous avez créé 20 notes',
                    'icone': 'bi-journal-text',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Preneur de Notes !")
    
    elif type_verification == 'evenement':
        # Trophée Événement - 10 événements créés
        nb_evenements = Evenement.objects.filter(id_foyer=foyer).count()
        if nb_evenements >= 10:
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='evenement',
                defaults={
                    'nom': '📅 Organisateur',
                    'description': 'Vous avez créé 10 événements',
                    'icone': 'bi-calendar-event',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Organisateur !")
    
    elif type_verification == 'explorateur':
        # Trophée Explorateur - A visité toutes les pièces
        pieces_foyer = Piece.objects.filter(id_foyer=foyer).count()
        if pieces_foyer >= 5:  # Au moins 5 pièces différentes
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='explorateur',
                defaults={
                    'nom': '🏠 Explorateur',
                    'description': 'Vous avez visité toutes les pièces de la maison',
                    'icone': 'bi-house-door',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Explorateur !")
    
    elif type_verification == 'streak_30':
        # Trophée Streak 30 jours
        dates_completion = Tache.objects.filter(
            id_foyer=foyer,
            complete_par=utilisateur,
            terminee=True,
            date_limite__isnull=False
        ).values_list('date_limite', flat=True).distinct().order_by('-date_limite')[:30]
        
        if len(dates_completion) >= 30:
            dates_list = list(dates_completion)
            est_streak = True
            for i in range(29):
                if dates_list[i] - dates_list[i+1] != timedelta(days=1):
                    est_streak = False
                    break
            if est_streak:
                trophee, created = Trophee.objects.get_or_create(
                    id_user=utilisateur,
                    type='streak_30',
                    defaults={
                        'nom': '🔥 Streak de 30 jours',
                        'description': 'Vous avez complété des tâches 30 jours consécutifs',
                        'icone': 'bi-fire',
                        'debloque': True
                    }
                )
                if created:
                    trophee_created = trophee
                    if request:
                        messages.success(request, "🎉 Trophée débloqué : Streak de 30 jours !")
    
    elif type_verification == 'streak_100':
        # Trophée Streak 100 jours
        dates_completion = Tache.objects.filter(
            id_foyer=foyer,
            complete_par=utilisateur,
            terminee=True,
            date_limite__isnull=False
        ).values_list('date_limite', flat=True).distinct().order_by('-date_limite')[:100]
        
        if len(dates_completion) >= 100:
            dates_list = list(dates_completion)
            est_streak = True
            for i in range(99):
                if dates_list[i] - dates_list[i+1] != timedelta(days=1):
                    est_streak = False
                    break
            if est_streak:
                trophee, created = Trophee.objects.get_or_create(
                    id_user=utilisateur,
                    type='streak_100',
                    defaults={
                        'nom': '🔥🔥 Streak de 100 jours',
                        'description': 'Vous avez complété des tâches 100 jours consécutifs !',
                        'icone': 'bi-fire',
                        'debloque': True
                    }
                )
                if created:
                    trophee_created = trophee
                    if request:
                        messages.success(request, "🎉 Trophée débloqué : Streak de 100 jours !")
    
    elif type_verification == 'organise':
        # Trophée Organisé - 50 tâches complétées à l'avance
        aujourdhui = timezone.now().date()
        taches_avance = Tache.objects.filter(
            id_foyer=foyer,
            complete_par=utilisateur,
            terminee=True,
            date_limite__gt=aujourdhui
        ).count()
        if taches_avance >= 50:
            trophee, created = Trophee.objects.get_or_create(
                id_user=utilisateur,
                type='organise',
                defaults={
                    'nom': '📋 Organisé',
                    'description': 'Vous avez complété 50 tâches à l\'avance',
                    'icone': 'bi-clipboard-check',
                    'debloque': True
                }
            )
            if created:
                trophee_created = trophee
                if request:
                    messages.success(request, "🎉 Trophée débloqué : Organisé !")
    
    return trophee_created

# === FONCTION HELPER POUR RÉCUPÉRER ET VALIDER UNE PIÈCE ===
def get_piece_or_redirect(request, piece_id):
    """
    Récupère une pièce et vérifie qu'elle appartient à un foyer de l'utilisateur.
    Définit automatiquement le foyer actif si nécessaire.
    Retourne (piece, None) si tout est OK, ou (None, HttpResponseRedirect) en cas d'erreur.
    """
    try:
        piece = Piece.objects.get(id=piece_id)
    except Piece.DoesNotExist:
        messages.error(request, "Cette pièce n'existe pas.")
        return None, redirect('liste_foyers')
    
    # Vérifier que la pièce appartient au moins à un foyer de l'utilisateur
    foyer = piece.id_foyer
    if foyer not in request.user.foyers.all() and request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette pièce.")
        return None, redirect('liste_foyers')
    
    # Définir le foyer actif si ce n'est pas déjà le cas
    if request.user.foyer_actif != foyer:
        request.user.foyer_actif = foyer
        request.user.save()
    
    # Vérifier les restrictions d'accès (si l'admin a restreint l'accès à cette pièce)
    if piece.utilisateurs_autorises.exists():
        if request.user not in piece.utilisateurs_autorises.all():
            # Vérifier si l'utilisateur est admin du foyer
            from .permissions import has_permission
            if not has_permission(request.user, 'can_manage_foyer'):
                messages.error(request, "Vous n'avez pas accès à cette pièce.")
                return None, redirect('detail_foyer', foyer_id=foyer.id)
    
    return piece, None


# === CONNEXION PERSONNALISÉE ===
def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirection : Dashboard si foyer actif, sinon profil
                if user.foyer_actif:
                    next_url = request.GET.get('next', '/dashboard/')
                else:
                    next_url = request.GET.get('next', '/mon_profil/')
                return redirect(next_url)
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# === VUES PROTÉGÉES ===
@login_required
def liste_taches(request):
    # Filtre par foyer actif de l'utilisateur (sécurité)
    if not request.user.foyer_actif:
        messages.info(request, "Vous devez sélectionner un foyer actif pour voir les tâches.")
        return render(request, 'maison_app/liste_taches.html', {
            'taches_aujourdhui': Tache.objects.none(),
            'taches_urgentes': Tache.objects.none(),
            'taches_actives': Tache.objects.none(),
            'statuts': StatutTache.objects.all(),
            'pieces': Piece.objects.none(),
            'recherche': '',
            'filtre_priorite': '',
            'filtre_statut': '',
            'filtre_piece': '',
        })
    
    # Récupérer les filtres depuis les paramètres GET
    recherche = request.GET.get('recherche', '')
    filtre_priorite = request.GET.get('priorite', '')
    filtre_statut = request.GET.get('statut', '')
    filtre_piece = request.GET.get('piece', '')
    
    # Base queryset : toutes les tâches du foyer actif non terminées
    taches = Tache.objects.filter(
        id_foyer=request.user.foyer_actif,
        terminee=False
    ).select_related('id_piece', 'id_animal', 'id_statut', 'complete_par').prefetch_related('tacheassignee_set__id_user')
    
    # Appliquer les filtres
    if recherche:
        taches = taches.filter(
            Q(titre__icontains=recherche) | Q(description__icontains=recherche)
        )
    
    if filtre_priorite:
        taches = taches.filter(priorite=filtre_priorite)
    
    if filtre_statut:
        taches = taches.filter(id_statut__libelle=filtre_statut)
    
    if filtre_piece:
        taches = taches.filter(id_piece_id=filtre_piece)
    
    # Catégoriser les tâches
    from datetime import timedelta
    aujourdhui = timezone.now().date()
    dans_2_jours = aujourdhui + timedelta(days=2)
    
    # Tâches à faire aujourd'hui (avec date_limite = aujourd'hui)
    taches_aujourdhui = taches.filter(date_limite=aujourdhui)
    
    # Tâches urgentes (dans les 2 prochains jours, mais pas aujourd'hui)
    taches_urgentes = taches.filter(
        date_limite__gt=aujourdhui,
        date_limite__lte=dans_2_jours
    )
    
    # Tâches actives (toutes les autres tâches non terminées : sans date ou date > dans 2 jours)
    taches_actives = taches.filter(
        Q(date_limite__isnull=True) | Q(date_limite__gt=dans_2_jours)
    )
    
    # Récupérer les statuts et pièces pour les filtres
    statuts = StatutTache.objects.all()
    pieces = Piece.objects.filter(id_foyer=request.user.foyer_actif)
    
    return render(request, 'maison_app/liste_taches.html', {
        'taches_aujourdhui': taches_aujourdhui,
        'taches_urgentes': taches_urgentes,
        'taches_actives': taches_actives,
        'statuts': statuts,
        'pieces': pieces,
        'recherche': recherche,
        'filtre_priorite': filtre_priorite,
        'filtre_statut': filtre_statut,
        'filtre_piece': filtre_piece,
    })
@login_required
def liste_foyers(request):
    if request.method == 'POST' and 'foyer_id' in request.POST:
        if request.user.role != 'admin':
            messages.error(request, "Accès refusé.")
            return redirect('liste_foyers')

        foyer_id = request.POST['foyer_id']
        nom_piece = request.POST['nom_piece']
        foyer = get_object_or_404(Foyer, id=foyer_id)

        Piece.objects.create(nom=nom_piece, id_foyer=foyer)
        messages.success(request, f"Pièce '{nom_piece}' ajoutée !")
        return redirect('liste_foyers')

    # AFFICHE UNIQUEMENT LES FOYERS DE L'UTILISATEUR
    # Tous les utilisateurs (y compris admins) voient uniquement leurs propres foyers
    # Seuls les superusers/staff peuvent voir tous les foyers
    if request.user.is_staff or request.user.is_superuser:
        # Les superusers/staff voient TOUS les foyers (pour administration)
        foyers = Foyer.objects.prefetch_related('pieces', 'animaux')
    else:
        # Tous les autres (y compris admins) voient uniquement leurs foyers
        foyers = request.user.foyers.prefetch_related('pieces', 'animaux')

    return render(request, 'maison_app/liste_foyers.html', {'foyers': foyers})
@login_required
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'maison_app/liste_utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def ajouter_tache(request):
    if not request.user.foyer_actif:
        messages.error(request, "Vous devez sélectionner un foyer actif.")
        return redirect('liste_foyers')

    if request.method == 'POST':
        titre = request.POST['titre']
        description = request.POST.get('description', '')
        date_limite = request.POST.get('date_limite')
        priorite = request.POST.get('priorite')
        id_statut = request.POST.get('id_statut')
        id_piece = request.POST.get('id_piece')
        id_animal = request.POST.get('id_animal')

        statut = StatutTache.objects.get(id=id_statut) if id_statut else StatutTache.objects.first()
        piece = Piece.objects.get(id=id_piece) if id_piece else None
        animal = Animal.objects.get(id=id_animal) if id_animal else None

        tache = Tache(
            titre=titre,
            description=description,
            date_limite=date_limite,
            priorite=priorite,
            id_statut=statut,
            id_foyer=request.user.foyer_actif,
            id_piece=piece,
            id_animal=animal
        )
        tache.save()
        
        # ✅ Traiter les assignations et créer des notifications
        assignees = request.POST.getlist('assignees')
        for assignee_id in assignees:
            try:
                assignee = Utilisateur.objects.get(id=assignee_id)
                if assignee in request.user.foyer_actif.utilisateurs.all():
                    # Créer l'assignation
                    TacheAssignee.objects.create(
                        id_tache=tache,
                        id_user=assignee
                    )
                    # ✅ Créer une notification pour l'utilisateur assigné
                    Notification.objects.create(
                        id_user=assignee,
                        type='tache_assignee',
                        titre=f"📋 Nouvelle tâche: {tache.titre}",
                        message=f"Vous avez été assigné à la tâche '{tache.titre}' par {request.user.nom or request.user.email}",
                        id_tache=tache,
                        id_foyer=request.user.foyer_actif
                    )
            except Utilisateur.DoesNotExist:
                pass
        
        messages.success(request, "✅ Tâche ajoutée et notifications envoyées !")
        return redirect('liste_taches')

    statuts = StatutTache.objects.all()
    pieces = Piece.objects.filter(id_foyer=request.user.foyer_actif)
    animaux = Animal.objects.filter(id_foyer=request.user.foyer_actif)
    membres = request.user.foyer_actif.utilisateurs.all()
    
    # Tâches prédéfinies
    taches_predefinies = [
        {'titre': 'Faire la vaisselle', 'description': 'Laver et ranger la vaisselle', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Passer l\'aspirateur', 'description': 'Nettoyer les sols avec l\'aspirateur', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Faire les courses', 'description': 'Acheter les produits nécessaires', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Sortir les poubelles', 'description': 'Sortir les poubelles pour la collecte', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Faire la lessive', 'description': 'Laver et étendre le linge', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Nettoyer la salle de bain', 'description': 'Nettoyer la douche, lavabo et WC', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Faire le lit', 'description': 'Refaire le lit proprement', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Ranger la chambre', 'description': 'Ranger et organiser la chambre', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Préparer le repas', 'description': 'Cuisiner le repas du jour', 'piece_id': None, 'piece_nom': None},
        {'titre': 'Arroser les plantes', 'description': 'Arroser les plantes d\'intérieur et d\'extérieur', 'piece_id': None, 'piece_nom': None},
    ]
    
    # Ajouter les pièces spécifiques si disponibles
    for piece in pieces:
        if piece.nom.lower() in ['cuisine', 'salle de bain', 'chambre', 'salon', 'salle à manger']:
            piece_nom = piece.nom
            if piece.nom.lower() == 'cuisine':
                taches_predefinies.append({
                    'titre': f'Nettoyer la {piece_nom}',
                    'description': f'Nettoyer et ranger la {piece_nom}',
                    'piece_id': piece.id,
                    'piece_nom': piece_nom
                })
            elif piece.nom.lower() in ['salle de bain', 'salle de bains']:
                taches_predefinies.append({
                    'titre': f'Nettoyer la {piece_nom}',
                    'description': f'Nettoyer la douche, lavabo et WC',
                    'piece_id': piece.id,
                    'piece_nom': piece_nom
                })
    
    # Récupérer les préférences des membres
    from .models import PreferenceUtilisateur
    preferences_membres = {}
    for membre in membres:
        prefs = PreferenceUtilisateur.objects.filter(
            id_user=membre,
            preference='aime'
        ).values_list('type_tache', flat=True)
        preferences_membres[membre.id] = list(prefs)
    
    # Générer les suggestions pour chaque tâche prédéfinie
    suggestions_predefinies = {}
    for index, tache_predef in enumerate(taches_predefinies):
        # Déterminer le type de tâche basé sur le titre/description
        texte = (tache_predef['titre'] + ' ' + tache_predef.get('description', '')).lower()
        type_tache = None
        
        mots_cles_nettoyage = ['nettoyer', 'nettoyage', 'aspirateur', 'aspirer', 'lessive', 'laver', 'ranger', 'propre', 'salle de bain', 'douche', 'wc', 'toilette', 'vitre', 'fenêtre', 'poubelle', 'sortir les poubelles', 'faire le lit', 'chambre']
        mots_cles_cuisine = ['cuisine', 'cuisiner', 'repas', 'dîner', 'déjeuner', 'préparer', 'vaisselle', 'lave-vaisselle', 'cuire', 'four', 'plaque', 'manger']
        mots_cles_courses = ['courses', 'acheter', 'magasin', 'supermarché', 'épicerie', 'produits', 'aliments', 'nourriture', 'faire les courses']
        mots_cles_entretien = ['entretien', 'réparer', 'réparation', 'maintenance', 'jardin', 'plante', 'arroser', 'tondeuse', 'outil', 'jardinage']
        
        if any(mot in texte for mot in mots_cles_nettoyage):
            type_tache = 'nettoyage'
        elif any(mot in texte for mot in mots_cles_cuisine):
            type_tache = 'cuisine'
        elif any(mot in texte for mot in mots_cles_courses):
            type_tache = 'courses'
        elif any(mot in texte for mot in mots_cles_entretien):
            type_tache = 'entretien'
        
        # Trouver les utilisateurs qui aiment ce type de tâche
        suggestions = []
        if type_tache:
            for membre in membres:
                if membre.id in preferences_membres and type_tache in preferences_membres[membre.id]:
                    suggestions.append(membre.id)
        
        suggestions_predefinies[index] = suggestions
    
    return render(request, 'maison_app/ajouter_tache.html', {
        'statuts': statuts,
        'pieces': pieces,
        'animaux': animaux,
        'membres': membres,
        'taches_predefinies': taches_predefinies,
        'suggestions_predefinies': suggestions_predefinies,
        'preferences_membres': preferences_membres,
    })

@login_required
def detail_tache(request, tache_id):
    """Affiche les détails d'une tâche"""
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.foyer_actif)
    
    # Gérer l'ajout de commentaire
    if request.method == 'POST' and 'ajouter_commentaire' in request.POST:
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            commentaire = CommentaireTache.objects.create(
                id_tache=tache,
                id_user=request.user,
                contenu=contenu
            )
            
            # Créer des notifications pour l'admin, la personne assignée et la personne qui a commencé la tâche
            foyer = tache.id_foyer
            # Set pour éviter les doublons de notifications
            utilisateurs_deja_notifies = {request.user.id}
            
            # Notifier tous les admins du foyer
            admins = foyer.utilisateurs.filter(role='admin')
            for admin in admins:
                if admin.id not in utilisateurs_deja_notifies:
                    Notification.objects.create(
                        id_user=admin,
                        type='commentaire_tache',
                        titre=f"💬 Commentaire sur la tâche: {tache.titre}",
                        message=f"{request.user.nom or request.user.email} a ajouté un commentaire sur la tâche '{tache.titre}'",
                        id_tache=tache,
                        id_foyer=foyer
                    )
                    utilisateurs_deja_notifies.add(admin.id)
            
            # Notifier toutes les personnes assignées à la tâche
            assignations = TacheAssignee.objects.filter(id_tache=tache).select_related('id_user')
            for assignation in assignations:
                if assignation.id_user.id not in utilisateurs_deja_notifies:
                    Notification.objects.create(
                        id_user=assignation.id_user,
                        type='commentaire_tache',
                        titre=f"💬 Commentaire sur votre tâche: {tache.titre}",
                        message=f"{request.user.nom or request.user.email} a ajouté un commentaire sur la tâche '{tache.titre}' qui vous est assignée",
                        id_tache=tache,
                        id_foyer=foyer
                    )
                    utilisateurs_deja_notifies.add(assignation.id_user.id)
            
            # Notifier la personne qui a commencé/complété la tâche si différente de l'auteur du commentaire
            if tache.complete_par and tache.complete_par.id not in utilisateurs_deja_notifies:
                Notification.objects.create(
                    id_user=tache.complete_par,
                    type='commentaire_tache',
                    titre=f"💬 Commentaire sur votre tâche: {tache.titre}",
                    message=f"{request.user.nom or request.user.email} a ajouté un commentaire sur la tâche '{tache.titre}' que vous avez commencée",
                    id_tache=tache,
                    id_foyer=foyer
                )
                utilisateurs_deja_notifies.add(tache.complete_par.id)
            
            messages.success(request, "Commentaire ajouté avec succès !")
            return redirect('detail_tache', tache_id=tache.id)
    
    # Récupérer les assignations
    assignations = TacheAssignee.objects.filter(id_tache=tache).select_related('id_user')
    
    # Récupérer les commentaires
    commentaires = CommentaireTache.objects.filter(id_tache=tache).select_related('id_user').order_by('-date_creation')
    
    return render(request, 'maison_app/detail_tache.html', {
        'tache': tache,
        'assignations': assignations,
        'commentaires': commentaires
    })

@login_required
def modifier_tache(request, tache_id):
    """Modifie une tâche existante"""
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.foyer_actif)
    
    if request.method == 'POST':
        tache.titre = request.POST.get('titre', tache.titre)
        tache.description = request.POST.get('description', tache.description)
        date_limite = request.POST.get('date_limite')
        if date_limite:
            tache.date_limite = date_limite
        tache.priorite = request.POST.get('priorite', tache.priorite)
        
        id_statut = request.POST.get('id_statut')
        if id_statut:
            tache.id_statut = StatutTache.objects.get(id=id_statut)
        
        id_piece = request.POST.get('id_piece')
        if id_piece:
            tache.id_piece = Piece.objects.get(id=id_piece) if id_piece else None
        else:
            tache.id_piece = None
        
        id_animal = request.POST.get('id_animal')
        if id_animal:
            tache.id_animal = Animal.objects.get(id=id_animal) if id_animal else None
        else:
            tache.id_animal = None
        
        tache.save()
        
        # Gérer les assignations
        assignees = request.POST.getlist('assignees')
        # Récupérer les assignations actuelles pour comparer
        anciennes_assignations = set(TacheAssignee.objects.filter(id_tache=tache).values_list('id_user_id', flat=True))
        nouvelles_assignations = set()
        
        # Supprimer les anciennes assignations
        TacheAssignee.objects.filter(id_tache=tache).delete()
        # Créer les nouvelles assignations
        for assignee_id in assignees:
            try:
                assignee = Utilisateur.objects.get(id=assignee_id)
                if assignee in request.user.foyer_actif.utilisateurs.all():
                    TacheAssignee.objects.create(id_tache=tache, id_user=assignee)
                    nouvelles_assignations.add(assignee_id)
                    # Créer une notification seulement pour les nouvelles assignations
                    if int(assignee_id) not in anciennes_assignations:
                        Notification.objects.create(
                            id_user=assignee,
                            type='tache_assignee',
                            titre=f"📋 Tâche assignée: {tache.titre}",
                            message=f"Vous avez été assigné à la tâche '{tache.titre}' par {request.user.nom or request.user.email}",
                            id_tache=tache,
                            id_foyer=request.user.foyer_actif
                        )
            except (Utilisateur.DoesNotExist, ValueError):
                pass
        
        messages.success(request, "✅ Tâche modifiée avec succès !")
        return redirect('detail_tache', tache_id=tache.id)
    
    statuts = StatutTache.objects.all()
    pieces = Piece.objects.filter(id_foyer=request.user.foyer_actif)
    animaux = Animal.objects.filter(id_foyer=request.user.foyer_actif)
    membres = request.user.foyer_actif.utilisateurs.all()
    assignations_actuelles = TacheAssignee.objects.filter(id_tache=tache).values_list('id_user_id', flat=True)
    
    return render(request, 'maison_app/modifier_tache.html', {
        'tache': tache,
        'statuts': statuts,
        'pieces': pieces,
        'animaux': animaux,
        'membres': membres,
        'assignations_actuelles': list(assignations_actuelles)
    })

@login_required
def annuler_tache_terminee(request, tache_id):
    """Annule le statut terminé d'une tâche (réactive la tâche)"""
    from .permissions import has_permission
    
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.foyer_actif)
    
    if not tache.terminee:
        messages.error(request, "Cette tâche n'est pas terminée.")
        # Rediriger vers la page d'origine si possible
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('liste_taches')
    
    # Vérifier les permissions : membres/juniors ne peuvent réactiver que leurs propres tâches
    if not has_permission(request.user, 'can_reactivate_own_tache'):
        messages.error(request, "Vous n'avez pas la permission de réactiver cette tâche.")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('liste_taches')
    
    # Vérifier que l'utilisateur a le droit de réactiver (celui qui l'a complétée ou admin)
    if tache.complete_par and tache.complete_par != request.user and request.user.role != 'admin':
        messages.error(request, "Vous ne pouvez réactiver que les tâches que vous avez complétées.")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('liste_taches')
    
    tache.terminee = False
    tache.complete_par = None
    tache.save()
    
    messages.success(request, f"✅ Tâche '{tache.titre}' réactivée avec succès !")
    return redirect('liste_taches')

@login_required
def creer_foyer(request):
    # Tous les utilisateurs peuvent créer un foyer
    # Quand on crée un foyer, on devient automatiquement admin de ce foyer
    
    if request.method == 'POST':
        nom = request.POST['nom']
        description = request.POST.get('description', '')
        photo = request.FILES.get('photo')
        
        foyer = Foyer(nom=nom, description=description, cree_par=request.user)
        if photo:
            foyer.photo = photo
        foyer.save()

        # Associer l'utilisateur au foyer
        request.user.foyers.add(foyer)
        request.user.foyer_actif = foyer
        # Si l'utilisateur n'est pas déjà admin, le devenir (car il crée un foyer)
        if request.user.role != 'admin':
            request.user.role = 'admin'
        request.user.save()

        messages.success(request, f"Foyer '{nom}' créé ! Vous êtes maintenant administrateur de ce foyer.")
        return redirect('liste_foyers')
    
    return render(request, 'maison_app/creer_foyer.html')

@login_required
def modifier_foyer(request, foyer_id):
    """Modifie un foyer existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    foyer = get_object_or_404(Foyer, id=foyer_id)
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'ajouter_membre':
            # Ajouter un membre au foyer
            email_membre = request.POST.get('email_membre', '').strip()
            if email_membre:
                try:
                    membre = Utilisateur.objects.get(email=email_membre)
                    if membre not in foyer.utilisateurs.all():
                        membre.foyers.add(foyer)
                        messages.success(request, f"{membre.email} a été ajouté au foyer.")
                    else:
                        messages.warning(request, f"{membre.email} est déjà membre de ce foyer.")
                except Utilisateur.DoesNotExist:
                    messages.error(request, f"Aucun utilisateur trouvé avec l'email {email_membre}.")
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'supprimer_membre':
            # Retirer un membre du foyer
            membre_id = request.POST.get('membre_id')
            if membre_id:
                try:
                    membre = Utilisateur.objects.get(id=membre_id)
                    if membre in foyer.utilisateurs.all() and membre != request.user:
                        membre.foyers.remove(foyer)
                        # Si c'était le foyer actif, le changer
                        if membre.foyer_actif == foyer:
                            autres_foyers = membre.foyers.all()
                            if autres_foyers.exists():
                                membre.foyer_actif = autres_foyers.first()
                            else:
                                membre.foyer_actif = None
                            membre.save()
                        messages.success(request, f"{membre.email} a été retiré du foyer.")
                    else:
                        messages.error(request, "Vous ne pouvez pas vous retirer vous-même du foyer.")
                except Utilisateur.DoesNotExist:
                    messages.error(request, "Membre introuvable.")
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'modifier_animal':
            # Modifier un animal
            animal_id = request.POST.get('animal_id')
            nom_animal = request.POST.get('nom_animal', '').strip()
            piece_id = request.POST.get('piece_id')
            photo_animal = request.FILES.get('photo_animal')
            supprimer_photo_animal = request.POST.get('supprimer_photo_animal') == 'on'
            
            if animal_id and nom_animal:
                try:
                    animal = Animal.objects.get(id=animal_id, id_foyer=foyer)
                    animal.nom = nom_animal
                    
                    if piece_id:
                        piece = Piece.objects.get(id=piece_id, id_foyer=foyer)
                        animal.id_piece = piece
                    else:
                        animal.id_piece = None
                    
                    if supprimer_photo_animal:
                        animal.photo = None
                    elif photo_animal:
                        animal.photo = photo_animal
                    
                    animal.save()
                    messages.success(request, f"Animal '{animal.nom}' modifié avec succès !")
                except Animal.DoesNotExist:
                    messages.error(request, "Animal introuvable.")
                except Piece.DoesNotExist:
                    messages.error(request, "Pièce introuvable.")
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'supprimer_animal':
            # Supprimer un animal
            animal_id = request.POST.get('animal_id')
            if animal_id:
                try:
                    animal = Animal.objects.get(id=animal_id, id_foyer=foyer)
                    nom_animal = animal.nom
                    animal.delete()
                    messages.success(request, f"Animal '{nom_animal}' supprimé avec succès !")
                except Animal.DoesNotExist:
                    messages.error(request, "Animal introuvable.")
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'ajouter_piece':
            # Ajouter une pièce
            nom = request.POST.get('nom_piece', '').strip()
            # Prendre la valeur du select principal (type_piece)
            type_piece = (request.POST.get('type_piece', '') or '').strip()
            description = request.POST.get('description_piece', '').strip()
            photo = request.FILES.get('photo_piece')
            
            # Si type_piece est vide, utiliser la valeur par défaut
            if not type_piece:
                type_piece = 'personnalise'
            
            if not nom:
                messages.error(request, "❌ Le nom de la pièce est obligatoire.")
            elif len(nom) > 100:
                messages.error(request, "❌ Le nom est trop long (max 100 caractères).")
            else:
                try:
                    # Créer la pièce avec le type sélectionné
                    piece = Piece(
                        nom=nom,
                        id_foyer=foyer,
                        type_piece=type_piece,
                        description=description
                    )
                    if photo:
                        piece.photo = photo
                    piece.save()
                    
                    # Gérer les permissions
                    utilisateurs_autorises = request.POST.getlist('utilisateurs_autorises_piece')
                    if utilisateurs_autorises:
                        piece.utilisateurs_autorises.set(utilisateurs_autorises)
                    
                    messages.success(request, f"✅ Pièce '{nom}' ajoutée avec succès !")
                except Exception as e:
                    messages.error(request, f"❌ Erreur lors de l'ajout de la pièce : {str(e)}")
            
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'modifier_piece':
            # Modifier une pièce
            piece_id = request.POST.get('piece_id')
            nom = request.POST.get('nom_piece', '').strip()
            type_piece = request.POST.get('type_piece', 'personnalise')
            description = request.POST.get('description_piece', '').strip()
            photo = request.FILES.get('photo_piece')
            supprimer_photo = request.POST.get('supprimer_photo_piece') == 'on'
            
            if not piece_id:
                messages.error(request, "❌ Pièce non identifiée.")
            elif not nom:
                messages.error(request, "❌ Le nom de la pièce est obligatoire.")
            elif len(nom) > 100:
                messages.error(request, "❌ Le nom est trop long (max 100 caractères).")
            else:
                try:
                    piece = Piece.objects.get(id=piece_id, id_foyer=foyer)
                    ancien_nom = piece.nom
                    
                    piece.nom = nom
                    piece.type_piece = type_piece
                    piece.description = description
                    
                    if supprimer_photo:
                        piece.photo = None
                    elif photo:
                        piece.photo = photo
                    
                    piece.save()
                    
                    # Gérer les permissions
                    utilisateurs_autorises = request.POST.getlist('utilisateurs_autorises_piece')
                    piece.utilisateurs_autorises.set(utilisateurs_autorises)
                    
                    messages.success(request, f"✅ Pièce '{ancien_nom}' → '{nom}' modifiée avec succès !")
                except Piece.DoesNotExist:
                    messages.error(request, "❌ Pièce introuvable ou vous n'avez pas les permissions.")
                except Exception as e:
                    messages.error(request, f"❌ Erreur lors de la modification : {str(e)}")
            
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        elif action == 'supprimer_piece':
            # Supprimer une pièce
            piece_id = request.POST.get('piece_id')
            if piece_id:
                try:
                    piece = Piece.objects.get(id=piece_id, id_foyer=foyer)
                    nom_piece = piece.nom
                    piece.delete()
                    messages.success(request, f"Pièce '{nom_piece}' supprimée avec succès !")
                except Piece.DoesNotExist:
                    messages.error(request, "Pièce introuvable.")
            return redirect('modifier_foyer', foyer_id=foyer.id)
        
        else:
            # Modifier les informations du foyer
            nom = request.POST.get('nom', '').strip()
            description = request.POST.get('description', '').strip()
            photo = request.FILES.get('photo')
            supprimer_photo = request.POST.get('supprimer_photo') == 'on'
            
            if nom:
                foyer.nom = nom
            if description is not None:
                foyer.description = description
            if photo:
                foyer.photo = photo
            if supprimer_photo:
                foyer.photo = None
            
            foyer.save()
            messages.success(request, f"Foyer '{foyer.nom}' modifié avec succès !")
            return redirect('detail_foyer', foyer_id=foyer.id)
    
    # Récupérer tous les membres du foyer
    membres_foyer = foyer.utilisateurs.all()
    
    # Récupérer tous les animaux du foyer
    animaux_foyer = Animal.objects.filter(id_foyer=foyer)
    
    # Récupérer toutes les pièces du foyer
    pieces_foyer = Piece.objects.filter(id_foyer=foyer)
    
    return render(request, 'maison_app/modifier_foyer.html', {
        'foyer': foyer,
        'membres_foyer': membres_foyer,
        'animaux_foyer': animaux_foyer,
        'pieces_foyer': pieces_foyer
    })

@login_required
def ajouter_piece(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter une pièce.")
        return redirect('liste_foyers')

    if not request.user.foyer_actif:
        messages.error(request, "Vous devez d'abord créer un foyer.")
        return redirect('creer_foyer')

    foyer = request.user.foyer_actif
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        photo = request.FILES.get('photo')
        type_piece = request.POST.get('type_piece', 'personnalise')
        description = request.POST.get('description', '')
        
        # Traiter les valeurs vides comme personnalise
        if not type_piece or type_piece == '':
            type_piece = 'personnalise'
        
        # Si type prédéfini, utiliser le nom du type si le nom n'est pas fourni
        if type_piece != 'personnalise':
            from .models import TYPE_PIECE_CHOICES
            type_dict = dict(TYPE_PIECE_CHOICES)
            if not nom or nom.strip() == '':
                nom = type_dict.get(type_piece, type_piece)
        
        # Détecter automatiquement le type basé sur le nom si c'est personnalise
        if type_piece == 'personnalise' and nom:
            from .models import TYPE_PIECE_CHOICES
            nom_lower = nom.lower().strip()
            for value, label in TYPE_PIECE_CHOICES:
                if value != 'personnalise' and (nom_lower == label.lower() or nom_lower == value or nom_lower in label.lower()):
                    type_piece = value
                    break
        
        # Gérer les permissions
        utilisateurs_autorises = request.POST.getlist('utilisateurs_autorises')
        
        # Déterminer le type_piece final (utiliser 'personnalise' si personnalisé)
        type_piece_final = type_piece if type_piece != 'personnalise' else 'personnalise'
        
        piece = Piece(
            nom=nom, 
            id_foyer=foyer,
            type_piece=type_piece_final,
            description=description if description else ''
        )
        if photo:
            piece.photo = photo
        piece.save()
        
        # Ajouter les utilisateurs autorisés si spécifiés
        if utilisateurs_autorises:
            piece.utilisateurs_autorises.set(utilisateurs_autorises)
        
        messages.success(request, f"Pièce '{nom}' ajoutée !")
        return redirect('detail_foyer', foyer_id=foyer.id)

    foyer = request.user.foyer_actif
    from .models import TYPE_PIECE_CHOICES
    membres_foyer = foyer.utilisateurs.all()
    
    return render(request, 'maison_app/ajouter_piece.html', {
        'foyer': foyer,
        'TYPE_PIECE_CHOICES': TYPE_PIECE_CHOICES,
        'membres_foyer': membres_foyer
    })

@login_required
def ajouter_animal(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter un animal.")
        return redirect('liste_foyers')

    if not request.user.foyer_actif:
        messages.error(request, "Vous devez d'abord créer un foyer.")
        return redirect('creer_foyer')

    if request.method == 'POST':
        nom = request.POST['nom']
        photo = request.FILES.get('photo')
        id_piece = request.POST.get('id_piece')

        # Récupérez l'instance Piece (CORRIGÉ)
        piece = Piece.objects.get(id=id_piece) if id_piece else None

        animal = Animal(
            nom=nom,
            id_foyer=request.user.foyer_actif,
            id_piece=piece  # ← CORRIGÉ : instance Piece
        )
        if photo:
            animal.photo = photo
        animal.save()
        # ✅ Vérifier et débloquer trophée Animal
        verifier_et_debloquer_trophees(request.user, 'animal', request)
        messages.success(request, f"Animal '{nom}' ajouté !")
        return redirect('liste_foyers')

    pieces = Piece.objects.filter(id_foyer=request.user.foyer_actif)
    return render(request, 'maison_app/ajouter_animal.html', {'pieces': pieces})

@login_required
def supprimer_piece(request, piece_id):
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    from .permissions import has_permission
    if not has_permission(request.user, 'can_manage_foyer'):
        messages.error(request, "Seuls les administrateurs peuvent supprimer une pièce.")
        return redirect('detail_foyer', foyer_id=piece.id_foyer.id)
    
    if request.method == 'POST':
        nom = piece.nom
        foyer_id = piece.id_foyer.id
        piece.delete()
        messages.success(request, f"Pièce '{nom}' supprimée avec succès !")
        return redirect('detail_foyer', foyer_id=foyer_id)
    
    return render(request, 'maison_app/supprimer_piece.html', {'piece': piece})

@login_required
def supprimer_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer un animal.")
        return redirect('detail_foyer', foyer_id=animal.id_foyer.id)
    
    # Vérifier que l'utilisateur a accès à ce foyer
    if animal.id_foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    if request.method == 'POST':
        nom = animal.nom
        foyer_id = animal.id_foyer.id
        animal.delete()
        messages.success(request, f"Animal '{nom}' supprimé avec succès !")
        return redirect('detail_foyer', foyer_id=foyer_id)
    
    return render(request, 'maison_app/supprimer_animal.html', {'animal': animal})

@login_required
def supprimer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.id_foyer)

    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer une tâche.")
        return redirect('liste_taches')
    
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "Tâche supprimée avec succès !")
        return redirect('liste_taches')
    
    return render(request, 'maison_app/supprimer_tache.html', {'tache': tache})

@login_required
def supprimer_foyer(request, foyer_id):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer un foyer.")
        return redirect('liste_foyers')

    foyer = get_object_or_404(Foyer, id=foyer_id)

    if request.method == 'POST':
        nom = foyer.nom
        foyer.delete()
        messages.success(request, f"Foyer '{nom}' supprimé avec succès !")
        return redirect('liste_foyers')

    return render(request, 'maison_app/supprimer_foyer.html', {'foyer': foyer})

@login_required
def generer_invitation(request, foyer_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent inviter.")
        return redirect('liste_foyers')

    foyer = get_object_or_404(Foyer, id=foyer_id)
    
    # Récupérer toutes les invitations (utilisées et non utilisées) pour ce foyer
    toutes_invitations = Invitation.objects.filter(foyer=foyer).order_by('-date_creation')
    invitation_actuelle = Invitation.objects.filter(foyer=foyer, utilise=False).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'reutiliser':
            # Réutiliser une invitation existante (la réactiver)
            invitation_id = request.POST.get('invitation_id')
            try:
                invitation = Invitation.objects.get(id=invitation_id, foyer=foyer)
                invitation.utilise = False
                invitation.save()
                messages.success(request, f"Invitation '{invitation.code}' réactivée avec succès !")
            except Invitation.DoesNotExist:
                messages.error(request, "Invitation introuvable.")
            return redirect('generer_invitation', foyer_id=foyer_id)
        
        elif action == 'regenerer':
            # Supprimer l'ancienne invitation et en créer une nouvelle
            if invitation_actuelle:
                invitation_actuelle.delete()
            
            role = request.POST.get('role', 'membre')
            nom = request.POST.get('nom', '').strip()
            invitation = Invitation.objects.create(
                foyer=foyer,
                role=role,
                nom=nom if nom else None
            )
            messages.success(request, f"Nouveau code d'invitation généré : {invitation.code}")
        else:
            # Créer nouvelle invitation
            role = request.POST.get('role', 'membre')
            nom = request.POST.get('nom', '').strip()
            invitation = Invitation.objects.create(
                foyer=foyer,
                role=role,
                nom=nom if nom else None
            )
            messages.success(request, f"Code d'invitation : {invitation.code}")
        
        return redirect('generer_invitation', foyer_id=foyer_id)

    # Actualiser après POST
    toutes_invitations = Invitation.objects.filter(foyer=foyer).order_by('-date_creation')
    invitation_actuelle = Invitation.objects.filter(foyer=foyer, utilise=False).first()

    return render(request, 'maison_app/generer_invitation.html', {
        'foyer': foyer,
        'invitation_actuelle': invitation_actuelle,
        'toutes_invitations': toutes_invitations,
        'ROLE_CHOICES': ROLE_CHOICES
    })

@login_required
def liste_utilisateurs_par_foyer(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent voir cette page.")
        return redirect('liste_taches')

    foyers = Foyer.objects.all().prefetch_related('utilisateur_set')  # Charge les utilisateurs
    return render(request, 'maison_app/liste_utilisateurs_par_foyer.html', {'foyers': foyers})

@login_required
def statistiques_foyer(request, foyer_id):
    """Affiche les statistiques d'un foyer"""
    foyer = get_object_or_404(Foyer, id=foyer_id)
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    # Statistiques des tâches
    taches_total = Tache.objects.filter(id_foyer=foyer).count()
    taches_terminees = Tache.objects.filter(id_foyer=foyer, terminee=True).count()
    taches_en_attente = taches_total - taches_terminees
    
    # Statistiques par membre
    membres_stats = []
    for membre in foyer.utilisateurs.all():
        taches_membre = Tache.objects.filter(id_foyer=foyer, complete_par=membre, terminee=True).count()
        membres_stats.append({
            'membre': membre,
            'taches_completes': taches_membre
        })
    
    return render(request, 'maison_app/statistiques_foyer.html', {
        'foyer': foyer,
        'taches_total': taches_total,
        'taches_terminees': taches_terminees,
        'taches_en_attente': taches_en_attente,
        'membres_stats': membres_stats
    })

@login_required
def statistiques_membre(request, user_id=None):
    """Affiche les statistiques d'un membre"""
    if user_id:
        membre = get_object_or_404(Utilisateur, id=user_id)
        if membre not in request.user.foyer_actif.utilisateurs.all():
            messages.error(request, "Accès refusé.")
            return redirect('dashboard')
    else:
        membre = request.user
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif.")
        return redirect('liste_foyers')
    
    # Statistiques
    taches_completes = Tache.objects.filter(id_foyer=foyer, complete_par=membre, terminee=True).count()
    taches_assignees = TacheAssignee.objects.filter(id_user=membre, id_tache__id_foyer=foyer).count()
    recompenses = Recompense.objects.filter(id_user=membre).count()
    points_totaux = sum(r.points for r in Recompense.objects.filter(id_user=membre))
    trophees = Trophee.objects.filter(id_user=membre, debloque=True).count()
    
    return render(request, 'maison_app/statistiques_membre.html', {
        'membre': membre,
        'foyer': foyer,
        'taches_completes': taches_completes,
        'taches_assignees': taches_assignees,
        'recompenses': recompenses,
        'points_totaux': points_totaux,
        'trophees': trophees
    })

@login_required
def detail_foyer(request, foyer_id):
    foyer = get_object_or_404(Foyer, id=foyer_id)
    # Vérifier que l'utilisateur est admin OU appartient bien au foyer
    if request.user.role != 'admin' and foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    # === AJOUT DE PIÈCE (POST) ===
    if request.method == 'POST' and 'nom_piece' in request.POST:
        if request.user.role != 'admin':
            messages.error(request, "Accès refusé.")
            return redirect('detail_foyer', foyer_id=foyer_id)

        nom = request.POST['nom_piece']
        piece = Piece(nom=nom, id_foyer=foyer)
        piece.save()
        messages.success(request, f"Pièce '{nom}' ajoutée !")
        return redirect('detail_foyer', foyer_id=foyer_id)

    # Charge le foyer + pièces/animaux
    foyer = Foyer.objects.prefetch_related('pieces', 'animaux').get(id=foyer_id)

    return render(request, 'maison_app/detail_foyer.html', {
        'foyer': foyer
    })
@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté !")
    return redirect('/taches/')  # ou '/' si vous voulez la page d'accueil

@login_required
def supprimer_membre(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    membre = get_object_or_404(Utilisateur, id=user_id)
    if request.user.foyer_actif not in membre.foyers.all():
        messages.error(request, "Ce membre n'appartient pas à votre foyer.")
        return redirect('liste_foyers')

    if request.method == 'POST':
        membre.foyers.remove(request.user.foyer_actif)
        messages.success(request, f"Membre {membre.email} supprimé !")
        return redirect('detail_foyer', foyer_id=request.user.foyer_actif.id)

    return render(request, 'maison_app/supprimer_membre.html', {'membre': membre})


def rejoindre_foyer(request, code=None):
    import re
    import uuid as uuid_lib
    
    # Si le code est passé dans l'URL (GET), l'utiliser directement
    if code:
        code_input = str(code)
    elif request.method == 'POST':
        code_input = request.POST.get('code', '').strip()
    else:
        # Afficher le formulaire de saisie
        return render(request, 'maison_app/rejoindre.html')
    
    if not code_input:
        messages.error(request, "Code d'invitation requis.")
        return render(request, 'maison_app/rejoindre.html')
    
    # Extraire l'UUID du code (peut être une URL complète ou juste l'UUID)
    code = None
    # Pattern pour trouver un UUID dans la chaîne
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(uuid_pattern, code_input, re.IGNORECASE)
    if match:
        code = match.group(0)
    else:
        # Si pas d'UUID trouvé, essayer de valider directement
        try:
            uuid_lib.UUID(code_input)
            code = code_input
        except (ValueError, AttributeError):
            pass
    
    if not code:
        messages.error(request, "Code d'invitation invalide. Veuillez entrer le code UUID ou l'URL complète.")
        return render(request, 'maison_app/rejoindre.html')
    
    # Si GET avec code et utilisateur connecté, traiter directement
    if request.method == 'GET' and code and request.user.is_authenticated:
        try:
            invitation = Invitation.objects.get(code=code, utilise=False)
            if invitation.est_valide():
                if invitation.foyer in request.user.foyers.all():
                    messages.error(request, "Vous appartenez déjà à ce foyer.")
                    return redirect('liste_foyers')
                
                # Associe l'utilisateur au foyer
                request.user.foyers.add(invitation.foyer)
                request.user.foyer_actif = invitation.foyer
                ancien_role = request.user.role
                request.user.role = invitation.role
                request.user.save()
                
                invitation.utilise = True
                invitation.save()
                
                # Créer une notification pour tous les autres membres
                foyer = invitation.foyer
                role_display = dict(ROLE_CHOICES).get(invitation.role, invitation.role)
                for utilisateur in foyer.utilisateurs.all():
                    if utilisateur != request.user:
                        Notification.objects.create(
                            id_user=utilisateur,
                            type='nouveau_membre',
                            titre=f"👥 Nouveau membre: {request.user.nom or request.user.email}",
                            message=f"{request.user.nom or request.user.email} a rejoint le foyer {foyer.nom} en tant que {role_display}",
                            id_foyer=foyer
                        )
                
                role_display = dict(ROLE_CHOICES).get(invitation.role, invitation.role)
                if ancien_role != invitation.role:
                    messages.success(request, f"Bienvenue dans le foyer {invitation.foyer.nom} ! Votre rôle a été défini sur '{role_display}' selon l'invitation.")
                else:
                    messages.success(request, f"Bienvenue dans le foyer {invitation.foyer.nom} !")
                return redirect('liste_taches')
            else:
                messages.error(request, "Code expiré ou déjà utilisé.")
        except Invitation.DoesNotExist:
            messages.error(request, "Code invalide.")
        except Exception as e:
            messages.error(request, f"Erreur lors du traitement de l'invitation : {str(e)}")
        # Si erreur, afficher le formulaire
        return render(request, 'maison_app/rejoindre.html', {'code_pre_rempli': code})
    
    # Si GET avec code mais utilisateur non connecté, afficher le formulaire pré-rempli
    if request.method == 'GET' and code:
        return render(request, 'maison_app/rejoindre.html', {'code_pre_rempli': code})
    
    if request.method == 'POST':
        # Si connecté, utilise les infos de l'utilisateur
        if request.user.is_authenticated:
            email = request.user.email
            nom = request.user.nom or request.user.email
        else:
            # Sinon, demande les infos
            nom = request.POST.get('nom', '')
            email = request.POST.get('email', '')

        try:
            invitation = Invitation.objects.get(code=code, utilise=False)
            if invitation.est_valide():
                # Si l'utilisateur est déjà connecté, on l'ajoute au foyer
                if request.user.is_authenticated:
                    if invitation.foyer in request.user.foyers.all():
                        messages.error(request, "Vous appartenez déjà à ce foyer.")
                        return redirect('liste_foyers')
                    
                    # Associe l'utilisateur au foyer
                    request.user.foyers.add(invitation.foyer)
                    request.user.foyer_actif = invitation.foyer
                    # ✅ IMPORTANT: Assigner le rôle de l'invitation à l'utilisateur
                    ancien_role = request.user.role
                    request.user.role = invitation.role
                    request.user.save()

                    invitation.utilise = True
                    invitation.save()
                    
                    # ✅ Créer une notification pour tous les autres membres
                    foyer = invitation.foyer
                    role_display = dict(ROLE_CHOICES).get(invitation.role, invitation.role)
                    for utilisateur in foyer.utilisateurs.all():
                        if utilisateur != request.user:
                            Notification.objects.create(
                                id_user=utilisateur,
                                type='nouveau_membre',
                                titre=f"👥 Nouveau membre: {request.user.nom or request.user.email}",
                                message=f"{request.user.nom or request.user.email} a rejoint le foyer {foyer.nom} en tant que {role_display}",
                                id_foyer=foyer
                            )

                    # Obtenir le nom du rôle depuis ROLE_CHOICES
                    role_display = dict(ROLE_CHOICES).get(invitation.role, invitation.role)
                    
                    if ancien_role != invitation.role:
                        messages.success(request, f"Bienvenue dans le foyer {invitation.foyer.nom} ! Votre rôle a été défini sur '{role_display}' selon l'invitation.")
                    else:
                        messages.success(request, f"Bienvenue dans le foyer {invitation.foyer.nom} !")
                    return redirect('liste_taches')
                
                # Sinon, crée un nouvel utilisateur
                else:
                    # Vérifie si l'email existe déjà
                    if Utilisateur.objects.filter(email=email).exists():
                        messages.error(request, "Cet email est déjà utilisé.")
                        return render(request, 'maison_app/rejoindre.html')

                    # Crée l'utilisateur avec username = email
                    utilisateur = Utilisateur(
                        username=email,
                        email=email,
                        nom=nom,
                        role=invitation.role
                    )
                    utilisateur.set_password('temporary123')  # Mot de passe temporaire
                    utilisateur.save()

                    # Associe l'utilisateur au foyer
                    utilisateur.foyers.add(invitation.foyer)
                    utilisateur.foyer_actif = invitation.foyer
                    utilisateur.save()

                    invitation.utilise = True
                    invitation.save()
                    
                    # ✅ Créer une notification pour tous les autres membres
                    foyer = invitation.foyer
                    for member in foyer.utilisateurs.all():
                        if member != utilisateur:
                            Notification.objects.create(
                                id_user=member,
                                type='nouveau_membre',
                                titre=f"👥 Nouveau membre: {nom}",
                                message=f"{nom} a rejoint le foyer {foyer.nom}",
                                id_foyer=foyer
                            )

                    # Obtenir le nom du rôle depuis ROLE_CHOICES
                    role_display = dict(ROLE_CHOICES).get(invitation.role, invitation.role)
                    messages.success(request, f"Bienvenue {nom} dans le foyer {invitation.foyer.nom} ! Votre rôle a été défini sur '{role_display}' selon l'invitation.")
                    login(request, utilisateur)  # Connexion automatique
                    return redirect('liste_taches')
            else:
                messages.error(request, "Code expiré ou déjà utilisé.")
        except Invitation.DoesNotExist:
            messages.error(request, "Code invalide.")
        except Exception as e:
            messages.error(request, f"Erreur lors du traitement de l'invitation : {str(e)}")
    
    return render(request, 'maison_app/rejoindre.html', {'code_pre_rempli': code if code else None})

@login_required
def terminer_tache(request, tache_id):
    from .permissions import has_permission
    
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.foyer_actif)
    if tache.terminee:
        messages.error(request, "Tâche déjà terminée.")
        return redirect('detail_foyer', foyer_id=tache.id_foyer.id)
    
    # Vérifier les permissions : membres/juniors ne peuvent terminer que leurs propres tâches
    if not has_permission(request.user, 'can_terminer_tache'):
        messages.error(request, "Vous n'avez pas la permission de terminer cette tâche.")
        return redirect('detail_tache', tache_id=tache.id)
    
    # Pour membres et juniors : vérifier que la tâche leur est assignée
    if request.user.role in ['membre', 'junior']:
        # Vérifier si la tâche est assignée à l'utilisateur
        est_assignee = TacheAssignee.objects.filter(
            id_tache=tache,
            id_user=request.user
        ).exists()
        
        # Vérifier si l'utilisateur a créé la tâche (via create_par si le champ existe)
        if not est_assignee:
            messages.error(request, "Vous ne pouvez terminer que les tâches qui vous sont assignées.")
            return redirect('detail_tache', tache_id=tache.id)

    tache.terminee = True
    tache.complete_par = request.user
    tache.save()
    
    # ✅ Créer une entrée dans l'historique
    HistoriqueTache.objects.create(
        id_tache=tache,
        id_user=request.user,
        date_execution=timezone.now()
    )
    
    # ✅ Créer une récompense pour l'utilisateur
    points = 50 if tache.priorite == 'Haute' else (30 if tache.priorite == 'Moyenne' else 10)
    recompense = Recompense.objects.create(
        id_user=request.user,
        type='points',
        nom=f"Tâche complétée: {tache.titre}",
        description=f"Vous avez complété la tâche '{tache.titre}'",
        points=points,
        icone='bi-check-circle',
        id_tache=tache
    )
    
    # ✅ Vérifier et créer des trophées - SYSTÈME AMÉLIORÉ
    nb_taches_completes = Tache.objects.filter(
        id_foyer=tache.id_foyer,
        complete_par=request.user,
        terminee=True
    ).count()
    
    # Trophées basés sur le nombre de tâches complétées
    trophées_nombre = {
        1: ('premier', '🏅 Première Tâche', 'Vous avez complété votre première tâche', 'bi-trophy'),
        10: ('10', '🏆 10 Tâches', 'Vous avez complété 10 tâches', 'bi-stars'),
        50: ('50', '⭐ 50 Tâches', 'Vous avez complété 50 tâches', 'bi-star-fill'),
        100: ('100', '👑 100 Tâches', 'Vous avez complété 100 tâches', 'bi-gem'),
        200: ('200', '💎 200 Tâches', 'Vous avez complété 200 tâches', 'bi-diamond'),
        500: ('500', '🌟 500 Tâches', 'Vous avez complété 500 tâches', 'bi-star-fill'),
        1000: ('1000', '👑 Maître Absolu', 'Vous avez complété 1000 tâches !', 'bi-trophy-fill'),
    }
    
    if nb_taches_completes in trophées_nombre:
        type_trophee, nom, description, icone = trophées_nombre[nb_taches_completes]
        trophee, created = Trophee.objects.get_or_create(
            id_user=request.user,
            type=type_trophee,
            defaults={
                'nom': nom,
                'description': description,
                'icone': icone,
                'debloque': True
            }
        )
        if created:
            messages.success(request, f"🎉 Trophée débloqué : {nom} !")
    
    # Trophée "Rapide" - Complété rapidement (désactivé car pas de date_creation dans le modèle)
    # Note: Ce trophée nécessiterait un champ date_creation dans le modèle Tache
    
    # Trophée "Efficace" - 10 tâches complétées en une journée
    aujourdhui = timezone.now().date()
    taches_aujourdhui = Tache.objects.filter(
        id_foyer=tache.id_foyer,
        complete_par=request.user,
        terminee=True,
        date_limite=aujourdhui
    ).count()
    if taches_aujourdhui == 10:
        trophee, created = Trophee.objects.get_or_create(
            id_user=request.user,
            type='efficace',
            defaults={
                'nom': '🔥 Efficace',
                'description': 'Vous avez complété 10 tâches en une seule journée',
                'icone': 'bi-fire',
                'debloque': True
            }
        )
        if created:
            messages.success(request, "🎉 Trophée débloqué : Efficace !")
    
    # Trophée "Punctuel" - Tâches complétées à temps (avant ou à la date limite)
    if tache.date_limite:
        aujourdhui_date = timezone.now().date()
        if aujourdhui_date <= tache.date_limite:
            taches_punctuel = Tache.objects.filter(
                id_foyer=tache.id_foyer,
                complete_par=request.user,
                terminee=True,
                date_limite__gte=aujourdhui_date
            ).count()
            if taches_punctuel == 50:
                trophee, created = Trophee.objects.get_or_create(
                    id_user=request.user,
                    type='punctuel',
                    defaults={
                        'nom': '⏰ Punctuel',
                        'description': 'Vous avez complété 50 tâches à temps',
                        'icone': 'bi-clock',
                        'debloque': True
                    }
                )
                if created:
                    messages.success(request, "🎉 Trophée débloqué : Punctuel !")
    
    # Trophée "Collaborateur" - Tâches assignées à d'autres
    taches_assignees = TacheAssignee.objects.filter(
        id_tache__id_foyer=tache.id_foyer,
        id_tache__terminee=True,
        id_user=request.user
    ).count()
    if taches_assignees == 20:
        trophee, created = Trophee.objects.get_or_create(
            id_user=request.user,
            type='collaborateur',
            defaults={
                'nom': '🤝 Collaborateur',
                'description': 'Vous avez complété 20 tâches assignées par d\'autres',
                'icone': 'bi-people',
                'debloque': True
            }
        )
        if created:
            messages.success(request, "🎉 Trophée débloqué : Collaborateur !")
    
    # Trophée "Streak" - 7 jours consécutifs
    from datetime import timedelta
    dates_completion = Tache.objects.filter(
        id_foyer=tache.id_foyer,
        complete_par=request.user,
        terminee=True,
        date_limite__isnull=False
    ).values_list('date_limite', flat=True).distinct().order_by('-date_limite')[:7]
    
    if len(dates_completion) >= 7:
        dates_list = list(dates_completion)
        est_streak = True
        for i in range(6):
            if dates_list[i] - dates_list[i+1] != timedelta(days=1):
                est_streak = False
                break
        if est_streak:
            trophee, created = Trophee.objects.get_or_create(
                id_user=request.user,
                type='streak',
                defaults={
                    'nom': '🔥 Streak de 7 jours',
                    'description': 'Vous avez complété des tâches 7 jours consécutifs',
                    'icone': 'bi-fire',
                    'debloque': True
                }
            )
            if created:
                messages.success(request, "🎉 Trophée débloqué : Streak de 7 jours !")
    
    # ✅ Vérifier les streaks 30 et 100 jours
    verifier_et_debloquer_trophees(request.user, 'streak_30', request)
    verifier_et_debloquer_trophees(request.user, 'streak_100', request)
    verifier_et_debloquer_trophees(request.user, 'organise', request)
    
    # ✅ Créer une notification pour tous les membres du foyer
    foyer = tache.id_foyer
    for utilisateur in foyer.utilisateurs.all():
        if utilisateur != request.user:  # Ne pas notifier celui qui complète
            Notification.objects.create(
                id_user=utilisateur,
                type='tache_complete',
                titre=f"✅ Tâche complétée: {tache.titre}",
                message=f"{request.user.nom or request.user.email} a complété la tâche '{tache.titre}' et a gagné {points} points",
                id_tache=tache,
                id_foyer=foyer
            )
    
    messages.success(request, f"✅ Tâche terminée ! +{points} points gagnés !")
    return redirect('detail_foyer', foyer_id=tache.id_foyer.id)
    
@login_required
def chat_foyer(request, foyer_id):
    foyer = get_object_or_404(Foyer, id=foyer_id)
    # Vérifier que l'utilisateur appartient bien au foyer (TOUS LES RÔLES PEUVENT ACCÉDER)
    if request.user.role != 'admin' and foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    messages_chat = ChatMessage.objects.filter(id_foyer=foyer).select_related('id_user')

    if request.method == 'POST':
        contenu = request.POST.get('message', '').strip()
        if contenu:
            msg = ChatMessage.objects.create(
                id_user=request.user,
                id_foyer=foyer,
                contenu=contenu
            )
            
            # ✅ Créer une notification pour tous les autres membres
            for utilisateur in foyer.utilisateurs.all():
                if utilisateur != request.user:  # Ne pas notifier l'auteur
                    Notification.objects.create(
                        id_user=utilisateur,
                        type='message',
                        titre=f"💬 Nouveau message de {request.user.nom or request.user.email}",
                        message=contenu[:100],  # Premier 100 caractères
                        id_foyer=foyer
                    )
            
            return redirect('chat_foyer', foyer_id=foyer_id)

    return render(request, 'maison_app/chat_foyer.html', {
        'foyer': foyer,
        'messages_chat': messages_chat
    })

@login_required
def api_send_message(request, foyer_id):
    """API pour envoyer un message dans le chat"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    foyer = get_object_or_404(Foyer, id=foyer_id)
    
    # Vérifier que l'utilisateur appartient au foyer
    if request.user.role != 'admin' and foyer not in request.user.foyers.all():
        return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
    
    # Vérifier que l'utilisateur n'est pas observateur
    if request.user.role == 'observateur':
        return JsonResponse({'success': False, 'error': 'Les observateurs ne peuvent pas envoyer de messages'}, status=403)
    
    contenu = request.POST.get('message', '').strip()
    fichier = request.FILES.get('fichier')
    
    if not contenu and not fichier:
        return JsonResponse({'success': False, 'error': 'Le message ne peut pas être vide'}, status=400)
    
    # Déterminer le type de fichier si un fichier est fourni
    type_fichier = None
    if fichier:
        ext = os.path.splitext(fichier.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            type_fichier = 'image'
        elif ext == '.pdf':
            type_fichier = 'pdf'
        else:
            type_fichier = 'autre'
    
    # Créer le message
    message = ChatMessage.objects.create(
        id_user=request.user,
        id_foyer=foyer,
        contenu=contenu if contenu else '',
        fichier=fichier if fichier else None,
        type_fichier=type_fichier if fichier else ''
    )
    
    # Créer des notifications pour les autres membres
    for utilisateur in foyer.utilisateurs.all():
        if utilisateur != request.user:
            Notification.objects.create(
                id_user=utilisateur,
                type='message',
                titre=f"💬 Nouveau message de {request.user.nom or request.user.email}",
                message=(contenu[:100] if contenu else 'Fichier partagé'),
                id_foyer=foyer
            )
    
    # Préparer la réponse
    message_data = {
        'id': message.id,
        'contenu': message.contenu,
        'date_envoi': message.date_envoi.isoformat(),
        'user': {
            'id': message.id_user.id,
            'nom': message.id_user.nom,
            'email': message.id_user.email,
            'photo_profil': message.id_user.photo_profil.url if message.id_user.photo_profil else None
        },
        'est_supprime': message.est_supprime,
        'est_modifie': message.est_modifie
    }
    
    if message.fichier:
        message_data['fichier'] = message.fichier.url
        message_data['nom_fichier'] = os.path.basename(message.fichier.name)
        message_data['type_fichier'] = message.type_fichier
    
    return JsonResponse({'success': True, 'message': message_data})

@login_required
def api_get_messages(request, foyer_id):
    """API pour récupérer les nouveaux messages"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    foyer = get_object_or_404(Foyer, id=foyer_id)
    
    # Vérifier que l'utilisateur appartient au foyer
    if request.user.role != 'admin' and foyer not in request.user.foyers.all():
        return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
    
    # Récupérer l'ID du dernier message connu
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0
    
    # Récupérer les nouveaux messages
    if last_id > 0:
        messages = ChatMessage.objects.filter(
            id_foyer=foyer,
            id__gt=last_id
        ).select_related('id_user').order_by('date_envoi')
    else:
        messages = ChatMessage.objects.filter(
            id_foyer=foyer
        ).select_related('id_user').order_by('date_envoi')[:50]  # Limiter à 50 messages si pas de last_id
    
    messages_data = []
    import os
    for msg in messages:
        is_own = msg.id_user == request.user if msg.id_user else False
        
        message_data = {
            'id': msg.id,
            'contenu': msg.contenu,
            'date_envoi': msg.date_envoi.isoformat(),
            'user': {
                'id': msg.id_user.id if msg.id_user else None,
                'nom': msg.id_user.nom if msg.id_user else 'Utilisateur supprimé',
                'email': msg.id_user.email if msg.id_user else '',
                'photo_profil': msg.id_user.photo_profil.url if msg.id_user and msg.id_user.photo_profil else None
            },
            'est_supprime': msg.est_supprime,
            'est_modifie': msg.est_modifie,
            'is_own': is_own
        }
        
        if msg.fichier:
            message_data['fichier'] = msg.fichier.url
            message_data['nom_fichier'] = os.path.basename(msg.fichier.name)
            message_data['type_fichier'] = msg.type_fichier
        
        messages_data.append(message_data)
    
    return JsonResponse({'success': True, 'messages': messages_data})

# === INSCRIPTION (NOUVELLE PAGE) ===
def inscription(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Validation de l'email : doit contenir @
        if '@' not in email:
            messages.error(request, "L'adresse email doit être valide et contenir un '@'.")
            return render(request, 'registration/inscription.html')

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'registration/inscription.html')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'registration/inscription.html')

        # Nouvel utilisateur = admin par défaut (peut créer un foyer)
        user = Utilisateur.objects.create_user(
            email=email,
            username=email,
            nom=nom,
            password=password,
            role='admin'
        )
        login(request, user)
        messages.success(request, f"Bienvenue {nom} ! Votre compte est créé. Vous êtes administrateur et pouvez créer un foyer.")
        return redirect('mon_profil')

    return render(request, 'registration/inscription.html')

# === MES NOTES ===
@login_required
def mes_notes(request):
    if request.method == 'POST':
        if 'ajouter' in request.POST:
            titre = request.POST.get('titre', '')
            contenu = request.POST.get('contenu', '')
            couleur_fond = request.POST.get('couleur_fond', '#FFF9C4')
            if titre and contenu:
                Note.objects.create(id_user=request.user, titre=titre, contenu=contenu, couleur_fond=couleur_fond)
                # ✅ Vérifier et débloquer trophée Note
                verifier_et_debloquer_trophees(request.user, 'note', request)
                messages.success(request, "Note ajoutée !")
            else:
                messages.error(request, "Titre et contenu requis.")
            return redirect('mes_notes')
        
        elif 'modifier' in request.POST:
            note_id = request.POST.get('note_id')
            titre = request.POST.get('titre', '')
            contenu = request.POST.get('contenu', '')
            couleur_fond = request.POST.get('couleur_fond', '#FFF9C4')
            note = get_object_or_404(Note, id=note_id, id_user=request.user)
            note.titre = titre
            note.contenu = contenu
            note.couleur_fond = couleur_fond
            note.save()
            messages.success(request, "Note modifiée !")
            return redirect('mes_notes')
        
        elif 'supprimer' in request.POST:
            note_id = request.POST.get('note_id')
            note = get_object_or_404(Note, id=note_id, id_user=request.user)
            note.delete()
            messages.success(request, "Note supprimée !")
            return redirect('mes_notes')
    
    notes = Note.objects.filter(id_user=request.user)
    return render(request, 'maison_app/mes_notes.html', {'notes': notes})

# === MON PROFIL ===
@login_required
def mon_profil(request):
    
    if request.method == 'POST':
        if 'creer_foyer' in request.POST:
            # Tous les utilisateurs peuvent créer un foyer depuis le modal du profil
            nom = request.POST.get('nom', '').strip()
            description = request.POST.get('description', '').strip()
            photo = request.FILES.get('photo')
            
            if not nom:
                messages.error(request, "Le nom du foyer est obligatoire.")
                return redirect('mon_profil')
            
            # Vérifier si un foyer avec ce nom existe déjà
            if Foyer.objects.filter(nom=nom).exists():
                messages.error(request, f"Un foyer avec le nom '{nom}' existe déjà.")
                return redirect('mon_profil')
            
            # Créer le foyer
            foyer = Foyer(nom=nom, description=description, cree_par=request.user)
            if photo:
                foyer.photo = photo
            foyer.save()
            
            # Associer l'utilisateur au foyer
            request.user.foyers.add(foyer)
            request.user.foyer_actif = foyer
            # Si l'utilisateur n'est pas déjà admin, le devenir (car il crée un foyer)
            if request.user.role != 'admin':
                request.user.role = 'admin'
            request.user.save()
            
            messages.success(request, f"Foyer '{nom}' créé avec succès ! Vous êtes maintenant administrateur de ce foyer.")
            return redirect('mon_profil')
        
        elif 'modifier_infos' in request.POST:
            nom = request.POST.get('nom', '')
            if nom:
                request.user.nom = nom
                request.user.save()
                messages.success(request, "Informations mises à jour !")
            return redirect('mon_profil')
        
        elif 'changer_foyer' in request.POST:
            foyer_id = request.POST.get('foyer_id')
            foyer = get_object_or_404(Foyer, id=foyer_id)
            # Vérifier que l'utilisateur appartient bien au foyer
            if foyer in request.user.foyers.all():
                request.user.foyer_actif = foyer
                request.user.save()
                messages.success(request, f"Vous êtes maintenant dans le foyer {foyer.nom} !")
            else:
                messages.error(request, "Vous n'appartenez pas à ce foyer.")
            return redirect('mon_profil')
        
        elif 'modifier_photo' in request.POST or 'photo_profil' in request.FILES:
            # Upload d'une photo de profil personnalisée
            photo_profil = request.FILES.get('photo_profil')
            if photo_profil:
                # Vérifier la taille (max 5MB)
                if photo_profil.size > 5 * 1024 * 1024:
                    messages.error(request, "La photo est trop volumineuse (max 5MB).")
                    return redirect('mon_profil')
                
                request.user.photo_profil = photo_profil
                request.user.save()
                messages.success(request, "Photo de profil mise à jour !")
                return redirect('mon_profil')
        
        elif 'avatar_selection' in request.POST:
            # Sélection d'un avatar depuis la galerie
            avatar_name = request.POST.get('avatar_selection', '').strip()
            if avatar_name:
                # Construire le chemin complet vers l'avatar
                avatar_path = settings.STATICFILES_DIRS[0] / 'images' / avatar_name
                if avatar_path.exists():
                    # Copier l'avatar vers le dossier media
                    from django.core.files import File
                    
                    media_dir = settings.MEDIA_ROOT / 'avatars'
                    media_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Créer un nom unique pour l'avatar copié
                    import uuid
                    unique_name = f"{uuid.uuid4()}_{avatar_name}"
                    
                    # Sauvegarder la référence dans photo_profil
                    with open(avatar_path, 'rb') as f:
                        request.user.photo_profil.save(unique_name, File(f), save=True)
                    
                    messages.success(request, "Avatar sélectionné avec succès !")
                else:
                    messages.error(request, "Avatar introuvable.")
            return redirect('mon_profil')
    
    # Récupérer tous les foyers de l'utilisateur
    foyers = request.user.foyers.all()
    
    # Déterminer le rôle dans le foyer actif
    role_dans_foyer_actif = None
    if request.user.foyer_actif:
        foyer_actif = request.user.foyer_actif
        # Vérifier si l'utilisateur a créé le foyer
        if foyer_actif.cree_par == request.user:
            # L'utilisateur a créé le foyer → admin
            role_dans_foyer_actif = 'admin'
        else:
            # L'utilisateur a rejoint le foyer → utiliser le rôle global (qui correspond au rôle de l'invitation)
            role_dans_foyer_actif = request.user.role
    else:
        # Pas de foyer actif, utiliser le rôle global
        role_dans_foyer_actif = request.user.role
    
    # Récupérer la liste des avatars disponibles
    avatars = []
    images_dir = settings.STATICFILES_DIRS[0] / 'images'
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            if filename.lower().startswith('avatar') and filename.lower().endswith('.png'):
                avatars.append(filename)
        avatars.sort()  # Trier par ordre alphabétique
    
    return render(request, 'maison_app/mon_profil.html', {
        'foyers': foyers,
        'foyer_actuel': request.user.foyer_actif,
        'avatars': avatars,
        'role_dans_foyer_actif': role_dans_foyer_actif
    })

# === DASHBOARD ===
@login_required
def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    
    if not request.user.foyer_actif:
        messages.error(request, "Sélectionnez d'abord un foyer.")
        return redirect('mon_profil')
    
    foyer = request.user.foyer_actif
    
    # Statistiques des tâches
    taches_total = Tache.objects.filter(id_foyer=foyer).count()
    taches_terminees = Tache.objects.filter(id_foyer=foyer, terminee=True).count()
    taches_en_attente = taches_total - taches_terminees
    
    # Tâches à venir (date limite dans les 7 prochains jours)
    date_limite_min = timezone.now()
    date_limite_max = timezone.now() + timedelta(days=7)
    taches_a_venir = Tache.objects.filter(
        id_foyer=foyer,
        terminee=False,
        date_limite__gte=date_limite_min,
        date_limite__lte=date_limite_max
    ).order_by('date_limite')[:5]
    
    # Tâches prioritaires (non terminées et priorité haute)
    taches_prioritaires = Tache.objects.filter(
        id_foyer=foyer,
        terminee=False,
        priorite='Haute'
    ).order_by('date_limite')[:5]
    
    # Tâches récentes
    taches_recentes = Tache.objects.filter(id_foyer=foyer).order_by('-id')[:5]
    
    # Statistiques par priorité
    stats_priorite = {
        'Haute': Tache.objects.filter(id_foyer=foyer, priorite='Haute', terminee=False).count(),
        'Moyenne': Tache.objects.filter(id_foyer=foyer, priorite='Moyenne', terminee=False).count(),
        'Basse': Tache.objects.filter(id_foyer=foyer, priorite='Basse', terminee=False).count(),
    }
    
    # Infos du foyer
    pieces = foyer.pieces.all().count()
    animaux = foyer.animaux.all().count()
    membres = foyer.utilisateurs.all().count()
    
    # Taux de complétion
    taux_completion = round((taches_terminees / taches_total * 100)) if taches_total > 0 else 0
    
    # Événements à venir (date_debut >= aujourd'hui, limité à 5)
    aujourdhui = timezone.now().date()
    evenements_a_venir = Evenement.objects.filter(
        id_foyer=foyer,
        date_debut__gte=aujourdhui
    ).order_by('date_debut')[:5]
    
    return render(request, 'maison_app/dashboard.html', {
        'foyer': foyer,
        'taches_total': taches_total,
        'taches_terminees': taches_terminees,
        'taches_en_attente': taches_en_attente,
        'taches_a_venir': taches_a_venir,
        'taches_prioritaires': taches_prioritaires,
        'taches_recentes': taches_recentes,
        'stats_priorite': stats_priorite,
        'pieces': pieces,
        'animaux': animaux,
        'membres': membres,
        'taux_completion': taux_completion,
        'evenements_a_venir': evenements_a_venir,
    })

# === NOTIFICATIONS ===
@login_required
def mes_notifications(request):
    """Affiche les notifications de l'utilisateur"""
    notifications = request.user.notifications.all().order_by('-date_creation')
    non_lues = request.user.notifications.filter(lue=False).count()
    
    return render(request, 'maison_app/mes_notifications.html', {
        'notifications': notifications,
        'non_lues': non_lues,
    })

@login_required
def marquer_notification_lue(request, id):
    """Marque une notification comme lue"""
    notification = get_object_or_404(Notification, id=id)
    if notification.id_user != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('mes_notifications')
    
    notification.lue = True
    notification.save()
    return redirect('mes_notifications')

@login_required
def supprimer_notification(request, id):
    """Supprime une notification"""
    notification = get_object_or_404(Notification, id=id)
    if notification.id_user != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('mes_notifications')
    
    notification.delete()
    messages.success(request, "Notification supprimée.")
    return redirect('mes_notifications')

# === BUDGET ET DÉPENSES ===
@login_required
def budget_foyer(request):
    """Affiche le dashboard des budgets et dépenses du foyer"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    # Vérifier la permission d'accès au budget
    if not has_permission(request.user, 'can_access_budget'):
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupère toutes les catégories avec leurs budgets
    categories = CategorieDepense.objects.all()
    budgets = Budget.objects.filter(id_foyer=foyer, actif=True)
    depenses_recentes = Depense.objects.filter(id_foyer=foyer).order_by('-date_depense')[:10]
    
    # Statistiques globales
    total_depenses = Depense.objects.filter(id_foyer=foyer).aggregate(total=Sum('montant'))['total'] or 0
    total_budget = budgets.aggregate(total=Sum('montant_limite'))['total'] or 0
    
    # Données pour les budgets
    budgets_data = []
    for budget in budgets:
        budgets_data.append({
            'budget': budget,
            'montant_utilise': budget.montant_utilise(),
            'pourcentage': budget.pourcentage_utilise(),
            'alerte': budget.alerte(),
        })
    
    # === DONNÉES POUR LES GRAPHIQUES ===
    from datetime import timedelta
    from django.utils import timezone
    import json
    
    today = timezone.now().date()
    
    # 1. Répartition des dépenses par catégorie (30 derniers jours)
    date_30_jours = today - timedelta(days=30)
    depenses_30_jours = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=date_30_jours
    )
    depenses_par_categorie_dict = {}
    for depense in depenses_30_jours:
        categorie_nom = depense.categorie.nom if depense.categorie else 'Autre'
        if categorie_nom not in depenses_par_categorie_dict:
            depenses_par_categorie_dict[categorie_nom] = 0
        depenses_par_categorie_dict[categorie_nom] += float(depense.montant)
    depenses_par_categorie = json.dumps(depenses_par_categorie_dict)
    
    # 2. Évolution des dépenses (6 derniers mois)
    evolution_depenses_dict = {}
    for i in range(6):
        # Calculer le mois (6 mois en arrière jusqu'à aujourd'hui)
        mois_cible = today.month - (5 - i)
        annee_cible = today.year
        
        # Gérer le cas où on dépasse l'année précédente
        while mois_cible < 1:
            mois_cible += 12
            annee_cible -= 1
        
        mois_debut = today.replace(month=mois_cible, year=annee_cible, day=1)
        
        # Calculer la fin du mois
        if i == 5:  # Mois actuel
            mois_fin = today
        else:
            # Fin du mois cible
            if mois_cible == 12:
                mois_fin = today.replace(month=1, year=annee_cible + 1, day=1) - timedelta(days=1)
            else:
                mois_fin = today.replace(month=mois_cible + 1, year=annee_cible, day=1) - timedelta(days=1)
        
        total_mois = Depense.objects.filter(
            id_foyer=foyer,
            date_depense__gte=mois_debut,
            date_depense__lte=mois_fin
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        mois_label = mois_debut.strftime('%m/%Y')
        evolution_depenses_dict[mois_label] = float(total_mois)
    evolution_depenses = json.dumps(evolution_depenses_dict)
    
    # 3. Comparaison Budget vs Dépenses par catégorie
    comparaison_dict = {}
    for categorie in categories:
        budget_cat = budgets.filter(categorie=categorie).aggregate(total=Sum('montant_limite'))['total'] or 0
        depenses_cat = Depense.objects.filter(
            id_foyer=foyer,
            categorie=categorie
        ).aggregate(total=Sum('montant'))['total'] or 0
        comparaison_dict[categorie.nom] = {
            'budget': float(budget_cat),
            'depenses': float(depenses_cat)
        }
    comparaison_budget_depenses = json.dumps(comparaison_dict)
    
    # 4. Dépenses par période
    lundi_semaine = today - timedelta(days=today.weekday())
    depenses_semaine = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=lundi_semaine
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    mois_debut = today.replace(day=1)
    depenses_mois = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=mois_debut
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    trimestre = (today.month - 1) // 3
    trimestre_debut = today.replace(month=trimestre * 3 + 1, day=1)
    depenses_trimestre = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=trimestre_debut
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    annee_debut = today.replace(month=1, day=1)
    depenses_annee = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=annee_debut
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # 5. Calcul du dépassement global
    budget_depasse = total_depenses > total_budget
    montant_depasse_global = total_depenses - total_budget if budget_depasse else 0
    
    return render(request, 'maison_app/budget_foyer.html', {
        'foyer': foyer,
        'budgets_data': budgets_data,
        'depenses_recentes': depenses_recentes,
        'total_depenses': total_depenses,
        'total_budget': total_budget,
        'depenses_par_categorie': depenses_par_categorie,
        'evolution_depenses': evolution_depenses,
        'comparaison_budget_depenses': comparaison_budget_depenses,
        'depenses_semaine': float(depenses_semaine),
        'depenses_mois': float(depenses_mois),
        'depenses_trimestre': float(depenses_trimestre),
        'depenses_annee': float(depenses_annee),
        'budget_depasse': budget_depasse,
        'montant_depasse_global': montant_depasse_global,
    })

@login_required
def ajouter_depense(request):
    """Ajoute une nouvelle dépense"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_create_depense'):
        messages.info(request, "Vous devez faire une demande pour créer une dépense.")
        return redirect('creer_demande')
    
    if request.method == 'POST':
        description = request.POST.get('description')
        montant = request.POST.get('montant')
        categorie_id = request.POST.get('categorie')
        date_depense = request.POST.get('date_depense')
        notes = request.POST.get('notes', '')
        
        try:
            categorie = CategorieDepense.objects.get(id=categorie_id)
            depense = Depense(
                id_foyer=foyer,
                description=description,
                montant=montant,
                categorie=categorie,
                id_user=request.user,
                date_depense=date_depense,
                notes=notes
            )
            depense.save()
            
            # ✅ Vérifier les budgets et créer des notifications d'alerte
            budgets = Budget.objects.filter(id_foyer=foyer, categorie=categorie, actif=True)
            for budget in budgets:
                pourcentage = budget.pourcentage_utilise()
                if pourcentage >= 100:
                    # Budget dépassé - URGENT
                    messages.error(request, f"🚨 ALERTE URGENTE: Budget '{categorie.nom}' DÉPASSÉ à {pourcentage}%!")
                    for utilisateur in foyer.utilisateurs.all():
                        Notification.objects.create(
                            id_user=utilisateur,
                            type='budget_alerte',
                            titre=f"🚨 URGENT - Budget dépassé: {categorie.nom}",
                            message=f"Le budget pour '{categorie.nom}' a été DÉPASSÉ ({pourcentage}%). Action immédiate recommandée!",
                            id_foyer=foyer
                        )
                elif pourcentage >= 80:
                    # Budget proche de la limite
                    messages.warning(request, f"⚠️ Attention: Budget '{categorie.nom}' à {pourcentage}%")
                    for utilisateur in foyer.utilisateurs.all():
                        Notification.objects.create(
                            id_user=utilisateur,
                            type='budget_alerte',
                            titre=f"⚠️ Budget proche: {categorie.nom}",
                            message=f"Le budget pour '{categorie.nom}' est à {pourcentage}%. Vigilance recommandée.",
                            id_foyer=foyer
                        )
            
            messages.success(request, "✅ Dépense ajoutée avec succès !")
            return redirect('budget_foyer')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    categories_principales = CategorieDepense.objects.filter(est_categorie_principale=True)
    return render(request, 'maison_app/ajouter_depense.html', {
        'foyer': foyer,
        'categories_principales': categories_principales,
    })

@login_required
def supprimer_depense(request, id):
    """Supprime une dépense"""
    depense = get_object_or_404(Depense, id=id)
    foyer = request.user.foyer_actif
    
    if depense.id_foyer != foyer or foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('budget_foyer')
    
    if request.method == 'POST':
        depense.delete()
        messages.success(request, "✅ Dépense supprimée.")
        return redirect('budget_foyer')
    
    return render(request, 'maison_app/supprimer_depense.html', {'depense': depense})

@login_required
def historique_depenses(request):
    """Affiche l'historique détaillé des dépenses par période"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Count, Avg
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    # Récupérer les paramètres de filtrage
    periode = request.GET.get('periode', 'mois')  # semaine, mois, trimestre, annee, tout
    categorie_id = request.GET.get('categorie', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    # Base queryset
    depenses = Depense.objects.filter(id_foyer=foyer).select_related('categorie', 'id_user').order_by('-date_depense')
    
    # Filtrer par période
    today = timezone.now().date()
    if periode == 'semaine':
        lundi = today - timedelta(days=today.weekday())
        depenses = depenses.filter(date_depense__gte=lundi)
        periode_label = f"Cette semaine (depuis {lundi.strftime('%d/%m/%Y')})"
    elif periode == 'mois':
        mois_debut = today.replace(day=1)
        depenses = depenses.filter(date_depense__gte=mois_debut)
        periode_label = f"Ce mois (depuis {mois_debut.strftime('%d/%m/%Y')})"
    elif periode == 'trimestre':
        trimestre = (today.month - 1) // 3
        trimestre_debut = today.replace(month=trimestre * 3 + 1, day=1)
        depenses = depenses.filter(date_depense__gte=trimestre_debut)
        periode_label = f"Ce trimestre (depuis {trimestre_debut.strftime('%d/%m/%Y')})"
    elif periode == 'annee':
        annee_debut = today.replace(month=1, day=1)
        depenses = depenses.filter(date_depense__gte=annee_debut)
        periode_label = f"Cette année (depuis {annee_debut.strftime('%d/%m/%Y')})"
    else:
        periode_label = "Toutes les dépenses"
    
    # Filtrer par catégorie
    if categorie_id:
        depenses = depenses.filter(categorie_id=categorie_id)
    
    # Filtrer par dates personnalisées
    if date_debut:
        depenses = depenses.filter(date_depense__gte=date_debut)
    if date_fin:
        depenses = depenses.filter(date_depense__lte=date_fin)
    
    # Pagination
    paginator = Paginator(depenses, 50)
    page = request.GET.get('page', 1)
    try:
        depenses_paginees = paginator.page(page)
    except PageNotAnInteger:
        depenses_paginees = paginator.page(1)
    except EmptyPage:
        depenses_paginees = paginator.page(paginator.num_pages)
    
    # Statistiques
    total = depenses.aggregate(total=Sum('montant'))['total'] or 0
    nombre_depenses = depenses.count()
    moyenne = depenses.aggregate(moyenne=Avg('montant'))['moyenne'] or 0
    
    # Dépenses par catégorie
    depenses_par_categorie = depenses.values('categorie__nom', 'categorie__couleur').annotate(
        total=Sum('montant'),
        nombre=Count('id')
    ).order_by('-total')
    
    # Dépenses par utilisateur
    depenses_par_utilisateur = depenses.values('id_user__nom', 'id_user__email').annotate(
        total=Sum('montant'),
        nombre=Count('id')
    ).order_by('-total')
    
    # Récupérer toutes les catégories pour le filtre
    categories = CategorieDepense.objects.all().order_by('nom')
    
    return render(request, 'maison_app/historique_depenses.html', {
        'depenses': depenses_paginees,
        'periode': periode,
        'periode_label': periode_label,
        'categorie_id': categorie_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total': float(total),
        'nombre_depenses': nombre_depenses,
        'moyenne': float(moyenne),
        'depenses_par_categorie': depenses_par_categorie,
        'depenses_par_utilisateur': depenses_par_utilisateur,
        'categories': categories,
        'foyer': foyer
    })

# === FONCTIONS STUB POUR LES FONCTIONNALITÉS NON ENCORE IMPLÉMENTÉES ===
@login_required
def export_budget_pdf(request):
    """Export du budget en PDF - À implémenter"""
    messages.info(request, "Fonctionnalité d'export PDF en cours de développement.")
    return redirect('budget_foyer')

@login_required
def export_budget_excel(request):
    """Export du budget en Excel - À implémenter"""
    messages.info(request, "Fonctionnalité d'export Excel en cours de développement.")
    return redirect('budget_foyer')

@login_required
def api_demandes_count(request):
    """API pour obtenir le nombre de demandes - À implémenter"""
    return JsonResponse({'count': 0})

@login_required
def api_delete_message(request, foyer_id, message_id):
    """API pour supprimer un message - À implémenter"""
    return JsonResponse({'success': False, 'message': 'Non implémenté'})

@login_required
def api_edit_message(request, foyer_id, message_id):
    """API pour éditer un message - À implémenter"""
    return JsonResponse({'success': False, 'message': 'Non implémenté'})

# === FONCTIONS STUB POUR FONCTIONNALITÉS AVANCÉES ===
@login_required
def demander_modification_date(request, tache_id):
    """Demande de modification de date - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('detail_tache', tache_id=tache_id)

@login_required
def gerer_demandes_modification(request):
    """Gérer les demandes de modification de dates"""
    from .models import DemandeModificationDate
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    # Récupérer les demandes en attente pour les tâches du foyer
    demandes = DemandeModificationDate.objects.filter(
        id_tache__id_foyer=foyer,
        statut='en_attente'
    ).select_related('id_tache', 'id_user').order_by('-date_creation')
    
    return render(request, 'maison_app/gerer_demandes_modification.html', {
        'demandes': demandes,
        'foyer': foyer
    })

@login_required
def traiter_demande_modification(request, demande_id, action):
    """Traiter une demande de modification - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('gerer_demandes_modification')

@login_required
def calendrier_taches(request):
    """Calendrier des tâches"""
    from datetime import datetime, timedelta
    from calendar import monthcalendar, monthrange
    from django.utils import timezone
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    # Récupérer le mois et l'année depuis les paramètres GET, sinon utiliser le mois actuel
    today = timezone.now().date()
    mois = int(request.GET.get('mois', today.month))
    annee = int(request.GET.get('annee', today.year))
    
    # Calculer le mois précédent et suivant
    if mois == 1:
        mois_precedent = 12
        annee_precedente = annee - 1
    else:
        mois_precedent = mois - 1
        annee_precedente = annee
    
    if mois == 12:
        mois_suivant = 1
        annee_suivante = annee + 1
    else:
        mois_suivant = mois + 1
        annee_suivante = annee
    
    # Récupérer les tâches du foyer avec dates limites dans ce mois
    taches = Tache.objects.filter(
        id_foyer=foyer,
        date_limite__year=annee,
        date_limite__month=mois
    ).select_related('id_statut')
    
    # Récupérer les événements du foyer qui se chevauchent avec ce mois
    # Un événement est dans le mois si :
    # - date_debut est dans le mois, OU
    # - date_fin est dans le mois, OU
    # - date_debut < début du mois ET date_fin > fin du mois (événement qui couvre tout le mois)
    from calendar import monthrange
    _, dernier_jour_mois = monthrange(annee, mois)
    debut_mois = datetime(annee, mois, 1).date()
    fin_mois = datetime(annee, mois, dernier_jour_mois).date()
    
    # Récupérer tous les événements qui se chevauchent avec ce mois
    # Un événement se chevauche si :
    # - date_debut <= fin_mois ET (date_fin >= debut_mois OU date_fin est NULL)
    # - Si date_fin est NULL, l'événement n'est affiché que le jour de début
    evenements = Evenement.objects.filter(
        id_foyer=foyer,
        date_debut__lte=fin_mois
    ).filter(
        Q(date_fin__gte=debut_mois) | Q(date_fin__isnull=True)
    )
    
    # Construire le calendrier
    calendrier = monthcalendar(annee, mois)
    semaines = []
    noms_mois = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    for semaine in calendrier:
        semaine_jours = []
        for jour_num in semaine:
            if jour_num == 0:
                # Jour du mois précédent ou suivant
                semaine_jours.append({
                    'numero': '',
                    'date': None,
                    'est_du_mois': False,
                    'taches': [],
                    'evenements': []
                })
            else:
                jour_date = datetime(annee, mois, jour_num).date()
                # date_limite est un DateField donc déjà un objet date, pas besoin de .date()
                jour_taches = [t for t in taches if t.date_limite and t.date_limite == jour_date]
                
                # Filtrer les événements qui sont actifs ce jour-là
                jour_evenements = []
                for e in evenements:
                    if e.date_debut:
                        # Si l'événement a une date de fin, vérifier que le jour est dans la plage [date_debut, date_fin]
                        if e.date_fin:
                            if e.date_debut <= jour_date <= e.date_fin:
                                jour_evenements.append(e)
                        else:
                            # Pas de date de fin, l'événement est seulement le jour de début
                            if e.date_debut == jour_date:
                                jour_evenements.append(e)
                
                semaine_jours.append({
                    'numero': jour_num,
                    'date': jour_date,
                    'est_du_mois': True,
                    'taches': jour_taches,
                    'evenements': jour_evenements
                })
        semaines.append(semaine_jours)
    
    return render(request, 'maison_app/calendrier_taches.html', {
        'semaines': semaines,
        'mois': mois,
        'annee': annee,
        'noms_mois': noms_mois,
        'mois_precedent': mois_precedent,
        'annee_precedente': annee_precedente,
        'mois_suivant': mois_suivant,
        'annee_suivante': annee_suivante,
        'today': today,
        'foyer': foyer
    })

@login_required
def liste_niveaux_snake(request, piece_id):
    """Liste des niveaux Snake disponibles"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'salle_de_jeux':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les salles de jeux.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Récupérer tous les niveaux actifs
    niveaux = NiveauSnake.objects.filter(actif=True).order_by('numero')
    
    # Récupérer les niveaux débloqués par l'utilisateur
    niveaux_debloques_ids = set(NiveauDebloque.objects.filter(id_user=request.user).values_list('id_niveau_id', flat=True))
    
    # Préparer les données des niveaux avec leur statut
    niveaux_data = []
    for niveau in niveaux:
        niveau_debloque = niveau.id in niveaux_debloques_ids
        niveau_gratuit = niveau.numero <= 2
        niveaux_data.append({
            'niveau': niveau,
            'debloque': niveau_debloque,
            'gratuit': niveau_gratuit,
            'accessible': niveau_debloque or niveau_gratuit
        })
    
    # Calculer les points totaux de l'utilisateur
    total_points = sum(r.points for r in Recompense.objects.filter(id_user=request.user))
    
    return render(request, 'maison_app/liste_niveaux_snake.html', {
        'piece': piece,
        'niveaux_data': niveaux_data,
        'niveaux_debloques': niveaux_debloques_ids,
        'total_points': total_points
    })

@login_required
def jouer_snake(request, piece_id, niveau_id):
    """Jouer au jeu Snake"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    niveau = get_object_or_404(NiveauSnake, id=niveau_id)
    
    # Vérifier si le niveau est débloqué ou gratuit
    niveau_debloque = NiveauDebloque.objects.filter(id_user=request.user, id_niveau=niveau).exists()
    niveau_gratuit = niveau.numero <= 2
    
    if not niveau_debloque and not niveau_gratuit:
        messages.error(request, "Ce niveau n'est pas débloqué.")
        return redirect('liste_niveaux_snake', piece_id=piece.id)
    
    # Récupérer ou créer l'entrée de déblocage pour suivre le meilleur score
    niveau_debloque_obj, created = NiveauDebloque.objects.get_or_create(
        id_user=request.user,
        id_niveau=niveau,
        defaults={'meilleur_score': 0}
    )
    
    return render(request, 'maison_app/jouer_snake.html', {
        'piece': piece,
        'niveau': niveau,
        'niveau_debloque': niveau_debloque_obj,
        'meilleur_score': niveau_debloque_obj.meilleur_score
    })

@login_required
def debloquer_niveau_snake(request, piece_id, niveau_id):
    """Débloquer un niveau Snake avec des points"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    niveau = get_object_or_404(NiveauSnake, id=niveau_id)
    
    # Vérifier si le niveau est gratuit
    if niveau.numero <= 2:
        messages.info(request, "Ce niveau est déjà gratuit.")
        return redirect('liste_niveaux_snake', piece_id=piece.id)
    
    # Vérifier si déjà débloqué
    if NiveauDebloque.objects.filter(id_user=request.user, id_niveau=niveau).exists():
        messages.info(request, "Ce niveau est déjà débloqué.")
        return redirect('liste_niveaux_snake', piece_id=piece.id)
    
    # Calculer les points disponibles
    total_points = sum(r.points for r in Recompense.objects.filter(id_user=request.user))
    
    if request.method == 'POST':
        if total_points >= niveau.points_deblocage:
            # Débloquer le niveau
            NiveauDebloque.objects.create(
                id_user=request.user,
                id_niveau=niveau
            )
            
            # Dépenser les points (créer une récompense négative)
            Recompense.objects.create(
                id_user=request.user,
                type='points',
                nom=f"Déblocage niveau Snake {niveau.numero}",
                description=f"Déblocage du niveau {niveau.nom}",
                points=-niveau.points_deblocage,
                icone='bi-unlock'
            )
            
            messages.success(request, f"Niveau {niveau.numero} débloqué !")
            return redirect('liste_niveaux_snake', piece_id=piece.id)
        else:
            messages.error(request, f"Points insuffisants. Il vous faut {niveau.points_deblocage} points.")
    
    return render(request, 'maison_app/debloquer_niveau_snake.html', {
        'piece': piece,
        'niveau': niveau,
        'total_points': total_points
    })

@login_required
def sauvegarder_score_snake(request, piece_id, niveau_id):
    """Sauvegarder le score Snake (API)"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return JsonResponse({'success': False, 'message': 'Accès refusé'})
    
    niveau = get_object_or_404(NiveauSnake, id=niveau_id)
    
    if request.method == 'POST':
        # Accepter FormData ou JSON
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            score = int(data.get('score', 0))
        else:
            score = int(request.POST.get('score', 0))
        
        niveau_debloque, created = NiveauDebloque.objects.get_or_create(
            id_user=request.user,
            id_niveau=niveau,
            defaults={'meilleur_score': 0}
        )
        
        score_ameliore = False
        points_gagnes = 0
        
        if score > niveau_debloque.meilleur_score:
            niveau_debloque.meilleur_score = score
            niveau_debloque.save()
            score_ameliore = True
            
            # Donner des points si le score requis est atteint
            if score >= niveau.score_requis:
                points_gagnes = 10
                Recompense.objects.create(
                    id_user=request.user,
                    type='points',
                    nom=f"Score Snake niveau {niveau.numero}",
                    description=f"Score de {score} au niveau {niveau.numero}",
                    points=points_gagnes,
                    icone='bi-trophy'
                )
        
        return JsonResponse({
            'success': True,
            'meilleur_score': niveau_debloque.meilleur_score,
            'score_ameliore': score_ameliore,
            'points_gagnes': points_gagnes
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def cuisine_view(request, piece_id):
    """Vue principale de la cuisine avec toutes les fonctionnalités"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    foyer = piece.id_foyer
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Récupérer les listes de courses récentes (si le modèle existe)
    listes_courses = []
    try:
        from .models import ListeCourses
        listes_courses = ListeCourses.objects.filter(id_piece=piece).order_by('-date_creation')[:5]
    except:
        pass
    
    # Récupérer le menu de la semaine actuel
    menu_semaine_actuel = None
    try:
        from .models import MenuSemaine
        today = timezone.now().date()
        menu_semaine_actuel = MenuSemaine.objects.filter(
            Q(id_piece=piece) | Q(id_foyer=foyer, id_piece__isnull=True),
            semaine_debut__lte=today,
            semaine_fin__gte=today
        ).first()
    except Exception as e:
        pass
    
    # Récupérer le nombre d'articles en stock
    inventaire_count = 0
    try:
        from .models import Inventaire
        inventaire_count = Inventaire.objects.filter(id_piece=piece).count()
    except:
        pass
    
    # Récupérer le nombre de recettes générées
    recettes_count = 0
    try:
        from .models import RecetteGeneree
        recettes_count = RecetteGeneree.objects.filter(id_piece=piece).count()
    except:
        pass
    
    return render(request, 'maison_app/cuisine.html', {
        'piece': piece,
        'foyer': foyer,
        'listes_courses': listes_courses,
        'menu_semaine_actuel': menu_semaine_actuel,
        'inventaire_count': inventaire_count,
        'recettes_count': recettes_count
    })

@login_required
def gerer_stock(request, piece_id):
    """Gérer le stock de la cuisine"""
    from .models import Inventaire
    from .permissions import has_permission
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer l'inventaire de la pièce
    inventaire = Inventaire.objects.filter(id_piece=piece).order_by('nom')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter_article':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            nom_article = request.POST.get('nom_article', '').strip()
            quantite = request.POST.get('quantite', '1')
            unite = request.POST.get('unite', '').strip()
            type_article = request.POST.get('type_article', 'aliment')
            
            if nom_article:
                try:
                    Inventaire.objects.create(
                        id_piece=piece,
                        id_foyer=piece.id_foyer,
                        nom=nom_article,
                        quantite=float(quantite) if quantite else 1,
                        unite=unite if unite else None,
                        type_article=type_article
                    )
                    messages.success(request, f"Article '{nom_article}' ajouté au stock.")
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'ajout: {str(e)}")
        
        elif action == 'modifier_quantite':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            article_id = request.POST.get('article_id')
            nouvelle_quantite = request.POST.get('nouvelle_quantite')
            try:
                article = Inventaire.objects.get(id=article_id, id_piece=piece)
                article.quantite = float(nouvelle_quantite) if nouvelle_quantite else 0
                if article.quantite > 0:
                    article.etat = 'disponible'
                article.save()
                messages.success(request, "Quantité mise à jour.")
            except Inventaire.DoesNotExist:
                messages.error(request, "Article introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        
        elif action == 'modifier_seuil':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            article_id = request.POST.get('article_id')
            quantite_alerte_min = request.POST.get('quantite_alerte_min')
            try:
                article = Inventaire.objects.get(id=article_id, id_piece=piece)
                article.quantite_alerte_min = float(quantite_alerte_min) if quantite_alerte_min else 1
                article.save()
                messages.success(request, "Seuil d'alerte mis à jour.")
            except Inventaire.DoesNotExist:
                messages.error(request, "Article introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        
        elif action == 'consommer':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            article_id = request.POST.get('article_id')
            quantite_consommee = request.POST.get('quantite_consommee', '1')
            try:
                article = Inventaire.objects.get(id=article_id, id_piece=piece)
                quantite_cons = float(quantite_consommee)
                if quantite_cons > 0 and article.quantite >= quantite_cons:
                    article.quantite -= quantite_cons
                    if article.quantite <= 0:
                        article.quantite = 0
                        article.etat = 'a_court'
                    article.save()
                    messages.success(request, f"Quantité consommée: {quantite_cons} {article.unite or ''}")
                else:
                    messages.error(request, "Quantité insuffisante.")
            except Inventaire.DoesNotExist:
                messages.error(request, "Article introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        
        elif action == 'a_court':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            article_id = request.POST.get('article_id')
            try:
                article = Inventaire.objects.get(id=article_id, id_piece=piece)
                article.etat = 'a_court'
                article.save()
                messages.success(request, "Article marqué comme 'à court'.")
            except Inventaire.DoesNotExist:
                messages.error(request, "Article introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        
        elif action == 'retirer':
            if not has_permission(request.user, 'can_modify_stock'):
                messages.error(request, "Vous n'avez pas la permission de modifier le stock.")
                return redirect('gerer_stock', piece_id=piece.id)
            
            article_id = request.POST.get('article_id')
            try:
                article = Inventaire.objects.get(id=article_id, id_piece=piece)
                nom = article.nom
                article.delete()
                messages.success(request, f"Article '{nom}' retiré du stock.")
            except Inventaire.DoesNotExist:
                messages.error(request, "Article introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        
        return redirect('gerer_stock', piece_id=piece.id)
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/gerer_stock.html', {
        'piece': piece,
        'foyer': foyer,
        'inventaire': inventaire
    })

@login_required
def api_get_weather(request):
    """API pour récupérer les données météo d'une ville"""
    city = request.GET.get('city', '').strip()
    
    if not city:
        return JsonResponse({'error': 'Ville non spécifiée'}, status=400)
    
    try:
        from .api_clients import get_weather_data
        
        weather_data = get_weather_data(city)
        
        if not weather_data:
            return JsonResponse({'error': 'Impossible de récupérer les données météo. Vérifiez que la clé API est configurée.'}, status=500)
        
        # Générer une recommandation vestimentaire basée sur la température
        temp = weather_data['temp']
        if temp >= 25:
            reco_text = "Il fait chaud ! Portez des vêtements légers."
            reco_tag = "tenue_ete"
            reco_class = "bg-danger"
        elif temp >= 15:
            reco_text = "Température agréable. Vêtements de mi-saison recommandés."
            reco_tag = "tenue_mi_saison"
            reco_class = "bg-success"
        elif temp >= 5:
            reco_text = "Il fait frais. Pensez à une veste ou un pull."
            reco_tag = "tenue_automne"
            reco_class = "bg-warning"
        else:
            reco_text = "Il fait froid ! Habillez-vous chaudement."
            reco_tag = "tenue_hiver"
            reco_class = "bg-info"
        
        return JsonResponse({
            'city': weather_data['city'],
            'temp': weather_data['temp'],
            'temp_min': weather_data['temp_min'],
            'temp_max': weather_data['temp_max'],
            'description': weather_data['description'],
            'icon': weather_data['icon'],
            'humidity': weather_data['humidity'],
            'wind_speed': weather_data['wind_speed'],
            'main': weather_data['main'],
            'reco_text': reco_text,
            'reco_tag': reco_tag,
            'reco_class': reco_class
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Erreur lors de la récupération de la météo: {str(e)}'}, status=500)

@login_required
def api_add_favorite_city(request):
    """API ajouter ville favorite"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    # Accepter les données en JSON ou en POST
    import json
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            city = data.get('city', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Données JSON invalides'})
    else:
        city = request.POST.get('city', '').strip()
    
    if not city:
        return JsonResponse({'success': False, 'message': 'Ville non spécifiée'})
    
    user = request.user
    favorites = user.villes_favorites_meteo if user.villes_favorites_meteo else []
    
    if city not in favorites:
        favorites.append(city)
        user.villes_favorites_meteo = favorites
        user.save()
        return JsonResponse({'success': True, 'message': f'{city} ajoutée aux favoris'})
    else:
        return JsonResponse({'success': False, 'message': f'{city} est déjà dans vos favoris'})

@login_required
def api_remove_favorite_city(request):
    """API retirer ville favorite"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    # Accepter les données en JSON ou en POST
    import json
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            city = data.get('city', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Données JSON invalides'})
    else:
        city = request.POST.get('city', '').strip()
    
    if not city:
        return JsonResponse({'success': False, 'message': 'Ville non spécifiée'})
    
    user = request.user
    favorites = user.villes_favorites_meteo if user.villes_favorites_meteo else []
    
    if city in favorites:
        favorites.remove(city)
        user.villes_favorites_meteo = favorites
        user.save()
        return JsonResponse({'success': True, 'message': f'{city} retirée des favoris'})
    else:
        return JsonResponse({'success': False, 'message': f'{city} n\'est pas dans vos favoris'})

@login_required
def liste_courses_cuisine(request, piece_id):
    """Liste de courses cuisine"""
    from .models import ListeCourses
    from .permissions import has_permission
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_liste_courses'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer les listes de courses de la pièce ou du foyer
    listes_courses = ListeCourses.objects.filter(
        Q(id_piece=piece) | Q(id_foyer=piece.id_foyer, id_piece__isnull=True)
    ).order_by('-date_creation')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'creer_liste':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de créer une liste.")
                return redirect('liste_courses_cuisine', piece_id=piece.id)
            
            nom_liste = request.POST.get('nom_liste', '').strip()
            if nom_liste:
                ListeCourses.objects.create(
                    nom=nom_liste,
                    id_foyer=piece.id_foyer,
                    id_piece=piece,
                    statut='En cours'
                )
                messages.success(request, f"Liste '{nom_liste}' créée avec succès !")
            return redirect('liste_courses_cuisine', piece_id=piece.id)
        
        elif action == 'supprimer_liste':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de supprimer une liste.")
                return redirect('liste_courses_cuisine', piece_id=piece.id)
            
            liste_id = request.POST.get('liste_id')
            try:
                liste = ListeCourses.objects.get(id=liste_id, id_foyer=piece.id_foyer)
                nom = liste.nom
                liste.delete()
                messages.success(request, f"Liste '{nom}' supprimée.")
            except ListeCourses.DoesNotExist:
                messages.error(request, "Liste introuvable.")
            return redirect('liste_courses_cuisine', piece_id=piece.id)
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/liste_courses_cuisine.html', {
        'piece': piece,
        'foyer': foyer,
        'listes_courses': listes_courses
    })

@login_required
def detail_liste_courses(request, piece_id, liste_id):
    """Détail liste de courses"""
    from .models import ListeCourses, Aliment
    from .permissions import has_permission
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    liste = get_object_or_404(ListeCourses, id=liste_id, id_foyer=piece.id_foyer)
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_liste_courses'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer les aliments de la liste
    aliments = Aliment.objects.filter(id_liste=liste).order_by('nom')
    
    # Calculer les statistiques
    total_aliments = aliments.count()
    aliments_achetes = aliments.filter(achete=True).count()
    pourcentage_achete = (aliments_achetes / total_aliments * 100) if total_aliments > 0 else 0
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter_aliment':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            nom_aliment = request.POST.get('nom_aliment', '').strip()
            if not nom_aliment:
                nom_aliment = request.POST.get('nom_element', '').strip()
            quantite = request.POST.get('quantite', '').strip()
            unite = request.POST.get('unite', '').strip()
            
            if nom_aliment:
                Aliment.objects.create(
                    id_liste=liste,
                    nom=nom_aliment,
                    quantite=float(quantite) if quantite else None,
                    unite=unite if unite else None
                )
                messages.success(request, f"Aliment '{nom_aliment}' ajouté à la liste.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'ajouter_element':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            nom_element = request.POST.get('nom_element', '').strip()
            quantite = request.POST.get('quantite', '').strip()
            unite = request.POST.get('unite', '').strip()
            
            if nom_element:
                Aliment.objects.create(
                    id_liste=liste,
                    nom=nom_element,
                    quantite=float(quantite) if quantite else None,
                    unite=unite if unite else None
                )
                messages.success(request, f"Élément '{nom_element}' ajouté à la liste.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'modifier_statut':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            nouveau_statut = request.POST.get('statut')
            if nouveau_statut in ['En cours', 'Acheté']:
                liste.statut = nouveau_statut
                liste.save()
                messages.success(request, f"Statut de la liste mis à jour: {nouveau_statut}")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'supprimer_aliment':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            aliment_id = request.POST.get('aliment_id')
            try:
                aliment = Aliment.objects.get(id=aliment_id, id_liste=liste)
                nom = aliment.nom
                aliment.delete()
                messages.success(request, f"Aliment '{nom}' retiré de la liste.")
            except Aliment.DoesNotExist:
                messages.error(request, "Aliment introuvable.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'toggle_achete':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            aliment_id = request.POST.get('aliment_id')
            try:
                aliment = Aliment.objects.get(id=aliment_id, id_liste=liste)
                aliment.achete = not aliment.achete
                aliment.save()
                
                # Si l'aliment est marqué comme acheté, l'ajouter au stock
                if aliment.achete:
                    from .models import Inventaire
                    from .permissions import has_permission as has_perm
                    
                    # Vérifier la permission de modifier le stock
                    if has_perm(request.user, 'can_modify_stock'):
                        # Vérifier si l'article existe déjà dans le stock
                        article_existant = Inventaire.objects.filter(
                            id_piece=piece,
                            nom__iexact=aliment.nom
                        ).first()
                        
                        if article_existant:
                            # Ajouter la quantité à l'article existant
                            quantite_ajouter = aliment.quantite if aliment.quantite else 1
                            article_existant.quantite += quantite_ajouter
                            article_existant.etat = 'disponible'
                            article_existant.save()
                            messages.success(request, f"Quantité de '{aliment.nom}' mise à jour dans le stock.")
                        else:
                            # Créer un nouvel article dans le stock
                            Inventaire.objects.create(
                                id_piece=piece,
                                id_foyer=piece.id_foyer,
                                nom=aliment.nom,
                                quantite=aliment.quantite if aliment.quantite else 1,
                                unite=aliment.unite if aliment.unite else None,
                                type_article='aliment',
                                etat='disponible'
                            )
                            messages.success(request, f"'{aliment.nom}' ajouté au stock.")
                    else:
                        messages.info(request, f"'{aliment.nom}' marqué comme acheté. (Pas de permission pour ajouter au stock)")
                
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            except Aliment.DoesNotExist:
                messages.error(request, "Aliment introuvable.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'tout_cocher':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            from .models import Inventaire
            from .permissions import has_permission as has_perm
            
            aliments_non_achetes = Aliment.objects.filter(id_liste=liste, achete=False)
            aliments_ajoutes = 0
            
            for aliment in aliments_non_achetes:
                aliment.achete = True
                aliment.save()
                
                # Ajouter au stock si permission
                if has_perm(request.user, 'can_modify_stock'):
                    article_existant = Inventaire.objects.filter(
                        id_piece=piece,
                        nom__iexact=aliment.nom
                    ).first()
                    
                    if article_existant:
                        quantite_ajouter = aliment.quantite if aliment.quantite else 1
                        article_existant.quantite += quantite_ajouter
                        article_existant.etat = 'disponible'
                        article_existant.save()
                    else:
                        Inventaire.objects.create(
                            id_piece=piece,
                            id_foyer=piece.id_foyer,
                            nom=aliment.nom,
                            quantite=aliment.quantite if aliment.quantite else 1,
                            unite=aliment.unite if aliment.unite else None,
                            type_article='aliment',
                            etat='disponible'
                        )
                    aliments_ajoutes += 1
            
            if aliments_ajoutes > 0:
                messages.success(request, f"Tous les éléments ont été cochés et {aliments_ajoutes} élément(s) ajouté(s) au stock.")
            else:
                messages.success(request, "Tous les éléments ont été cochés.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'tout_decocher':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            Aliment.objects.filter(id_liste=liste, achete=True).update(achete=False)
            messages.success(request, "Tous les éléments ont été décochés.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'marquer_achete':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            # Marquer tous les aliments comme achetés et ajouter au stock
            from .models import Inventaire
            from .permissions import has_permission as has_perm
            
            aliments_non_achetes = Aliment.objects.filter(id_liste=liste, achete=False)
            aliments_ajoutes = 0
            
            for aliment in aliments_non_achetes:
                aliment.achete = True
                aliment.save()
                
                if has_perm(request.user, 'can_modify_stock'):
                    article_existant = Inventaire.objects.filter(
                        id_piece=piece,
                        nom__iexact=aliment.nom
                    ).first()
                    
                    if article_existant:
                        quantite_ajouter = aliment.quantite if aliment.quantite else 1
                        article_existant.quantite += quantite_ajouter
                        article_existant.etat = 'disponible'
                        article_existant.save()
                    else:
                        Inventaire.objects.create(
                            id_piece=piece,
                            id_foyer=piece.id_foyer,
                            nom=aliment.nom,
                            quantite=aliment.quantite if aliment.quantite else 1,
                            unite=aliment.unite if aliment.unite else None,
                            type_article='aliment',
                            etat='disponible'
                        )
                    aliments_ajoutes += 1
            
            liste.statut = 'Acheté'
            liste.save()
            
            if aliments_ajoutes > 0:
                messages.success(request, f"Liste marquée comme achetée. {aliments_ajoutes} élément(s) ajouté(s) au stock.")
            else:
                messages.success(request, "Liste marquée comme achetée.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'ajouter_ingredients':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            ingredients_ids = request.POST.getlist('ingredients')
            if ingredients_ids:
                from .models import Ingredient
                ingredients = Ingredient.objects.filter(id__in=ingredients_ids)
                ajoutes = 0
                for ingredient in ingredients:
                    Aliment.objects.get_or_create(
                        id_liste=liste,
                        nom=ingredient.nom,
                        defaults={'quantite': None, 'unite': None}
                    )
                    ajoutes += 1
                messages.success(request, f"{ajoutes} ingrédient(s) ajouté(s) à la liste.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'modifier_liste':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de modifier la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            nouveau_nom = request.POST.get('nouveau_nom', '').strip()
            if nouveau_nom:
                liste.nom = nouveau_nom
                liste.save()
                messages.success(request, "Nom de la liste modifié.")
            return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
        
        elif action == 'supprimer_liste':
            if not has_permission(request.user, 'can_modify_liste_courses'):
                messages.error(request, "Vous n'avez pas la permission de supprimer la liste.")
                return redirect('detail_liste_courses', piece_id=piece.id, liste_id=liste.id)
            
            nom = liste.nom
            liste.delete()
            messages.success(request, f"Liste '{nom}' supprimée.")
            return redirect('liste_courses_cuisine', piece_id=piece.id)
    
    # Récupérer les ingrédients disponibles pour les suggestions
    from .models import Ingredient
    ingredients = Ingredient.objects.all().order_by('categorie', 'nom')
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/detail_liste_courses.html', {
        'piece': piece,
        'foyer': foyer,
        'liste': liste,
        'aliments': aliments,
        'total_aliments': total_aliments,
        'aliments_achetes': aliments_achetes,
        'pourcentage_achete': pourcentage_achete,
        'ingredients': ingredients
    })

@login_required
def menus_semaine(request, piece_id):
    """Menus de la semaine"""
    from .models import MenuSemaine
    from .permissions import has_permission
    from django.utils import timezone
    from datetime import timedelta
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_menus'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer les menus de la pièce ou du foyer
    menus = MenuSemaine.objects.filter(
        Q(id_piece=piece) | Q(id_foyer=piece.id_foyer, id_piece__isnull=True)
    ).order_by('-semaine_debut')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'creer_menu':
            if not has_permission(request.user, 'can_modify_menus'):
                messages.error(request, "Vous n'avez pas la permission de créer un menu.")
                return redirect('menus_semaine', piece_id=piece.id)
            
            semaine_debut_str = request.POST.get('semaine_debut')
            if semaine_debut_str:
                try:
                    from datetime import datetime
                    semaine_debut = datetime.strptime(semaine_debut_str, '%Y-%m-%d').date()
                    semaine_fin = semaine_debut + timedelta(days=6)
                    
                    # Vérifier si un menu existe déjà pour cette semaine
                    menu_existant = MenuSemaine.objects.filter(
                        id_foyer=piece.id_foyer,
                        semaine_debut=semaine_debut
                    ).first()
                    
                    if menu_existant:
                        messages.warning(request, f"Un menu existe déjà pour la semaine du {semaine_debut.strftime('%d/%m/%Y')}.")
                    else:
                        MenuSemaine.objects.create(
                            id_foyer=piece.id_foyer,
                            id_piece=piece,
                            semaine_debut=semaine_debut,
                            semaine_fin=semaine_fin,
                            cree_par=request.user
                        )
                        messages.success(request, f"Menu créé pour la semaine du {semaine_debut.strftime('%d/%m/%Y')} !")
                except Exception as e:
                    messages.error(request, f"Erreur lors de la création: {str(e)}")
            return redirect('menus_semaine', piece_id=piece.id)
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/menus_semaine.html', {
        'piece': piece,
        'foyer': foyer,
        'menus': menus
    })

@login_required
def detail_menu_semaine(request, piece_id, menu_id):
    """Détail et modification d'un menu de la semaine"""
    from .permissions import has_permission
    from .models import MenuSemaine, RepasMenu
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_menus'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer le menu
    try:
        menu = MenuSemaine.objects.get(id=menu_id, id_foyer=piece.id_foyer)
    except MenuSemaine.DoesNotExist:
        messages.error(request, "Ce menu n'existe pas.")
        return redirect('menus_semaine', piece_id=piece.id)
    
    # Récupérer les repas du menu
    repas = RepasMenu.objects.filter(id_menu=menu).order_by('jour', 'type_repas')
    
    # Jours de la semaine
    jours_semaine = RepasMenu.JOURS_SEMAINE
    
    # Plats prédéfinis par type de repas
    plats_predfinis = {
        'Petit-déjeuner': ['Café et croissants', 'Thé et tartines', 'Céréales et fruits', 'Œufs brouillés', 'Pancakes', 'Yaourt et fruits'],
        'Déjeuner': ['Salade composée', 'Pâtes carbonara', 'Riz et poulet', 'Poisson et légumes', 'Burger', 'Pizza', 'Tacos', 'Sushi'],
        'Dîner': ['Soupe et pain', 'Quiche', 'Gratin', 'Risotto', 'Tajine', 'Couscous', 'Lasagnes', 'Ratatouille'],
        'Collation': ['Fruits', 'Yaourt', 'Compote', 'Biscuits', 'Fromage', 'Noix']
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter_repas':
            if not has_permission(request.user, 'can_modify_menus'):
                messages.error(request, "Vous n'avez pas la permission de modifier ce menu.")
                return redirect('detail_menu_semaine', piece_id=piece.id, menu_id=menu.id)
            
            jour = request.POST.get('jour')
            type_repas = request.POST.get('type_repas')
            nom_repas = request.POST.get('nom_repas', '').strip()
            
            if jour and type_repas and nom_repas:
                RepasMenu.objects.create(
                    id_menu=menu,
                    jour=jour,
                    type_repas=type_repas,
                    nom=nom_repas,
                    description=request.POST.get('description', '')
                )
                messages.success(request, f"Repas '{nom_repas}' ajouté !")
            else:
                messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('detail_menu_semaine', piece_id=piece.id, menu_id=menu.id)
        
        elif action == 'supprimer_repas':
            if not has_permission(request.user, 'can_modify_menus'):
                messages.error(request, "Vous n'avez pas la permission de modifier ce menu.")
                return redirect('detail_menu_semaine', piece_id=piece.id, menu_id=menu.id)
            
            repas_id = request.POST.get('repas_id')
            try:
                repas_obj = RepasMenu.objects.get(id=repas_id, id_menu=menu)
                nom = repas_obj.nom
                repas_obj.delete()
                messages.success(request, f"Repas '{nom}' supprimé !")
            except RepasMenu.DoesNotExist:
                messages.error(request, "Repas introuvable.")
            return redirect('detail_menu_semaine', piece_id=piece.id, menu_id=menu.id)
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/detail_menu_semaine.html', {
        'piece': piece,
        'foyer': foyer,
        'menu': menu,
        'repas': repas,
        'jours_semaine': jours_semaine,
        'plats_predfinis': plats_predfinis
    })

@login_required
def generer_recettes(request, piece_id):
    """Générer des recettes à partir d'ingrédients du stock"""
    from .permissions import has_permission
    
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_view_recettes'):
        messages.error(request, "Vous n'avez pas accès à cette fonctionnalité.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    if not has_permission(request.user, 'can_generate_recettes'):
        messages.error(request, "Vous n'avez pas la permission de générer des recettes.")
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer les aliments du stock
    from .models import Inventaire, RecetteGeneree
    inventaire = Inventaire.objects.filter(id_piece=piece, etat='disponible').order_by('nom')
    
    # Récupérer les recettes générées récentes
    recettes = RecetteGeneree.objects.filter(id_piece=piece).order_by('-date_creation')[:10]
    
    recettes_api_data = None
    erreur = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generer_recettes':
            # Récupérer les ingrédients sélectionnés
            ingredients_ids = request.POST.getlist('ingredients')
            nombre_recettes = int(request.POST.get('nombre_recettes', 10))
            
            if not ingredients_ids:
                erreur = "Veuillez sélectionner au moins un ingrédient."
            else:
                # Récupérer les noms des ingrédients depuis le stock
                articles_selectionnes = Inventaire.objects.filter(id__in=ingredients_ids, id_piece=piece)
                noms_ingredients = [article.nom for article in articles_selectionnes]
                
                if not noms_ingredients:
                    erreur = "Aucun ingrédient valide trouvé."
                else:
                    try:
                        # Importer le module de traduction et l'API
                        from .traduction_ingredients import normaliser_ingredients
                        from .forkify_api import rechercher_recettes_par_ingredients, obtenir_details_recette
                        
                        # Normaliser les ingrédients (traduction en anglais si nécessaire)
                        ingredients_normalises = normaliser_ingredients(noms_ingredients)
                        
                        # Générer les recettes via l'API Forkify
                        recettes_api = rechercher_recettes_par_ingredients(ingredients_normalises, nombre_recettes)
                        
                        if recettes_api and len(recettes_api) > 0:
                            # Formater les recettes pour l'affichage
                            recettes_api_data = []
                            for recette_api in recettes_api:
                                try:
                                    # Obtenir l'ID de la recette
                                    recette_id = recette_api.get('id', '')
                                    if not recette_id:
                                        continue
                                    
                                    # Obtenir les détails complets de la recette
                                    details = obtenir_details_recette(recette_id)
                                    
                                    if details:
                                        # Formater les ingrédients depuis les détails
                                        ingredients_list = []
                                        for ing in details.get('ingredients', []):
                                            if isinstance(ing, dict):
                                                # Forkify utilise 'description' pour les ingrédients
                                                desc = ing.get('description', '')
                                                if not desc:
                                                    # Essayer de construire la description
                                                    quantity = ing.get('quantity', '')
                                                    unit = ing.get('unit', '')
                                                    desc = f"{quantity} {unit}".strip() if quantity or unit else ''
                                                if desc.strip():
                                                    ingredients_list.append(desc.strip())
                                            elif isinstance(ing, str):
                                                ingredients_list.append(ing)
                                        
                                        recette_formatee = {
                                            'id': str(recette_id),
                                            'titre': details.get('title', recette_api.get('title', 'Recette sans nom')),
                                            'image_url': details.get('image_url', recette_api.get('image_url', '')),
                                            'source_url': details.get('source_url', recette_api.get('source_url', '')),
                                            'readyInMinutes': details.get('cooking_time', recette_api.get('cooking_time', None)),
                                            'servings': details.get('servings', recette_api.get('servings', None)),
                                            'ingredients': ', '.join(ingredients_list) if ingredients_list else 'Ingrédients non disponibles',
                                            'instructions': details.get('instructions', '') or 'Consultez le lien source pour les instructions.',
                                        }
                                    else:
                                        # Utiliser les données de base si les détails ne sont pas disponibles
                                        recette_formatee = {
                                            'id': str(recette_id),
                                            'titre': recette_api.get('title', 'Recette sans nom'),
                                            'image_url': recette_api.get('image_url', recette_api.get('image', '')),
                                            'source_url': recette_api.get('source_url', ''),
                                            'readyInMinutes': recette_api.get('cooking_time', None),
                                            'servings': recette_api.get('servings', None),
                                            'ingredients': 'Ingrédients non disponibles',
                                            'instructions': 'Consultez le lien source pour les instructions.',
                                        }
                                    
                                    recettes_api_data.append(recette_formatee)
                                except Exception as e:
                                    # Continuer avec la recette suivante en cas d'erreur
                                    print(f"Erreur lors du formatage de la recette: {e}")
                                    continue
                            
                            if not recettes_api_data:
                                erreur = "Aucune recette trouvée avec ces ingrédients. Essayez avec d'autres ingrédients."
                            else:
                                # Stocker les recettes dans la session pour la sauvegarde
                                request.session['recettes_api_data'] = recettes_api_data
                                request.session['ingredients_recherche'] = ', '.join(noms_ingredients)
                                messages.success(request, f"{len(recettes_api_data)} recette(s) générée(s) avec succès !")
                        else:
                            erreur = "Aucune recette trouvée avec ces ingrédients. Essayez avec d'autres ingrédients ou vérifiez votre connexion internet."
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        erreur = f"Erreur lors de la génération des recettes: {str(e)}"
        
        elif action == 'sauvegarder_recettes':
            # Sauvegarder les recettes dans l'historique
            recettes_api_data = request.session.get('recettes_api_data', [])
            ingredients_recherche = request.session.get('ingredients_recherche', '')
            
            if recettes_api_data:
                recettes_sauvegardees = 0
                for recette_data in recettes_api_data:
                    try:
                        # Vérifier si la recette existe déjà
                        recette_existante = RecetteGeneree.objects.filter(
                            id_foyer=piece.id_foyer,
                            recette_id_api=recette_data.get('id', ''),
                            cree_par=request.user
                        ).first()
                        
                        if not recette_existante:
                            # Formater les ingrédients
                            ingredients_str = recette_data.get('ingredients', '')
                            if ingredients_str:
                                ingredients_details = [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]
                            else:
                                ingredients_details = []
                            
                            RecetteGeneree.objects.create(
                                id_foyer=piece.id_foyer,
                                id_piece=piece,
                                cree_par=request.user,
                                titre=recette_data.get('titre', 'Recette sans nom'),
                                recette_id_api=str(recette_data.get('id', '')),
                                image_url=recette_data.get('image_url', '') or None,
                                source_url=recette_data.get('source_url', '') or None,
                                temps_preparation=recette_data.get('readyInMinutes') or None,
                                portions=recette_data.get('servings') or None,
                                ingredients_recherche=ingredients_recherche,
                                ingredients_details=ingredients_details,
                                instructions=recette_data.get('instructions', '') or None
                            )
                            recettes_sauvegardees += 1
                    except Exception as e:
                        print(f"Erreur lors de la sauvegarde d'une recette: {e}")
                        continue
                
                # Nettoyer la session
                if 'recettes_api_data' in request.session:
                    del request.session['recettes_api_data']
                if 'ingredients_recherche' in request.session:
                    del request.session['ingredients_recherche']
                
                if recettes_sauvegardees > 0:
                    messages.success(request, f"{recettes_sauvegardees} recette(s) sauvegardée(s) dans l'historique !")
                else:
                    messages.info(request, "Ces recettes sont déjà sauvegardées dans l'historique.")
                return redirect('generer_recettes', piece_id=piece.id)
            else:
                erreur = "Aucune recette à sauvegarder."
    
    # Récupérer les recettes depuis la session si elles existent (pour l'affichage après POST)
    if recettes_api_data is None:
        recettes_api_data = request.session.get('recettes_api_data', None)
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/generer_recettes.html', {
        'piece': piece,
        'foyer': foyer,
        'recettes': recettes,
        'inventaire': inventaire,
        'recettes_api_data': recettes_api_data,
        'erreur': erreur
    })

@login_required
def historique_recettes(request, piece_id):
    """Historique des recettes générées"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    if piece.type_piece != 'cuisine':
        messages.error(request, "Cette fonctionnalité n'est disponible que pour les cuisines.")
        return redirect('detail_piece', piece_id=piece.id)
    
    # Récupérer toutes les recettes générées
    try:
        from .models import RecetteGeneree
        from django.core.paginator import Paginator
        recettes = RecetteGeneree.objects.filter(id_piece=piece).order_by('-date_creation')
        paginator = Paginator(recettes, 20)
        page = request.GET.get('page', 1)
        recettes_page = paginator.get_page(page)
    except:
        recettes_page = []
    
    foyer = piece.id_foyer
    return render(request, 'maison_app/historique_recettes.html', {
        'piece': piece,
        'foyer': foyer,
        'recettes': recettes_page
    })

@login_required
@login_required
def historique_taches(request):
    """Historique des tâches complétées"""
    foyer = request.user.foyer_actif
    
    if not foyer:
        return render(request, 'maison_app/historique_taches.html', {'foyer': None})
    
    # Récupérer l'historique des tâches complétées
    historique = HistoriqueTache.objects.filter(
        id_tache__id_foyer=foyer
    ).select_related('id_tache', 'id_user', 'id_tache__id_piece').order_by('-date_execution')
    
    # Filtrer par utilisateur si spécifié
    user_id = request.GET.get('user')
    if user_id:
        try:
            user_id = int(user_id)
            historique = historique.filter(id_user_id=user_id)
        except ValueError:
            pass
    
    # Calculer le total de complétions
    total_completions = HistoriqueTache.objects.filter(id_tache__id_foyer=foyer).count()
    
    # Récupérer les utilisateurs du foyer pour les filtres
    utilisateurs_foyer = foyer.utilisateurs.all()
    
    # Statistiques par utilisateur
    completions_par_user = HistoriqueTache.objects.filter(
        id_tache__id_foyer=foyer
    ).values('id_user__nom', 'id_user__email').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Récupérer aussi les tâches terminées (pour affichage et réactivation)
    taches_terminees = Tache.objects.filter(
        id_foyer=foyer,
        terminee=True
    ).select_related('id_piece', 'complete_par').order_by('-id')
    
    return render(request, 'maison_app/historique_taches.html', {
        'foyer': foyer,
        'historique': historique,
        'total_completions': total_completions,
        'utilisateurs_foyer': utilisateurs_foyer,
        'completions_par_user': completions_par_user,
        'taches_terminees': taches_terminees,
    })

@login_required
def suggestions_taches(request):
    """Suggestions de tâches - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('liste_taches')

@login_required
def recherche(request):
    """Recherche - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('dashboard')

@login_required
def proposer_suggestion(request):
    """Proposer une suggestion - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('suggestions_taches')

@login_required
def gerer_suggestion(request, suggestion_id):
    """Gérer une suggestion - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('suggestions_taches')

@login_required
def mes_preferences(request):
    """
    Page des préférences utilisateur
    
    Permet à l'utilisateur de gérer ses préférences personnelles
    (thème, notifications, langue, etc.)
    """
    user = request.user
    
    if request.method == 'POST':
        # Traitement des préférences (à implémenter selon les besoins)
        messages.success(request, "Préférences mises à jour avec succès !")
        return redirect('mes_preferences')
    
    return render(request, 'maison_app/mes_preferences.html', {
        'user': user
    })

@login_required
def mes_statistiques(request):
    """
    Page des statistiques personnelles de l'utilisateur
    
    Affiche les statistiques de l'utilisateur :
    - Nombre de tâches complétées
    - Points gagnés
    - Trophées débloqués
    - Activité récente
    """
    user = request.user
    foyer_actif = user.foyer_actif
    
    # Statistiques des tâches - Total
    total_taches = HistoriqueTache.objects.filter(id_user=user).count()
    
    # Tâches cette semaine
    debut_semaine = timezone.now() - timedelta(days=timezone.now().weekday())
    taches_semaine = HistoriqueTache.objects.filter(
        id_user=user,
        date_completion__gte=debut_semaine
    ).count()
    
    # Tâches ce mois
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    taches_mois = HistoriqueTache.objects.filter(
        id_user=user,
        date_completion__gte=debut_mois
    ).count()
    
    # Calcul du temps total (en secondes)
    historique_taches = HistoriqueTache.objects.filter(id_user=user)
    total_temps = timedelta()
    for hist in historique_taches:
        if hist.tache and hist.tache.duree_estimee:
            total_temps += hist.tache.duree_estimee
    
    # Points et récompenses
    total_points = Recompense.objects.filter(id_user=user, type='points').aggregate(
        total=Sum('points')
    )['total'] or 0
    
    # Trophées
    trophees_debloques = Trophee.objects.filter(id_user=user, debloque=True).count()
    total_trophees = Trophee.objects.filter(id_user=user).count()
    
    # Statistiques par jour (pour le graphique)
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    
    stats_par_jour = HistoriqueTache.objects.filter(
        id_user=user,
        date_completion__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        date_stat=TruncDate('date_completion')
    ).values('date_stat').annotate(
        nb_taches_done=Count('id')
    ).order_by('date_stat')
    
    # Préparer les données pour le graphique JavaScript
    dates = [str(stat['date_stat']) for stat in stats_par_jour]
    taches_par_jour = [stat['nb_taches_done'] for stat in stats_par_jour]
    
    # Statistiques détaillées (pour le tableau)
    stats_detaillees = []
    for stat in stats_par_jour:
        stats_detaillees.append({
            'date_stat': stat['date_stat'],
            'nb_taches_done': stat['nb_taches_done'],
            'temps_connexion': timedelta(hours=0)  # À implémenter si nécessaire
        })
    
    return render(request, 'maison_app/mes_statistiques.html', {
        'user': user,
        'foyer_actif': foyer_actif,
        'total_taches': total_taches,
        'taches_semaine': taches_semaine,
        'taches_mois': taches_mois,
        'total_points': total_points,
        'trophees_debloques': trophees_debloques,
        'total_trophees': total_trophees,
        'total_temps': total_temps,
        'stats': stats_detaillees,  # Le template utilise 'stats'
        'dates': json.dumps(dates),
        'taches_par_jour': json.dumps(taches_par_jour),
    })

@login_required
def liste_dispositifs(request):
    """Liste des dispositifs - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('dashboard')

@login_required
def ajouter_dispositif(request):
    """Ajouter un dispositif - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('liste_dispositifs')

@login_required
def modifier_dispositif(request, dispositif_id):
    """Modifier un dispositif - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('liste_dispositifs')

@login_required
def supprimer_dispositif(request, dispositif_id):
    """Supprimer un dispositif - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('liste_dispositifs')

@login_required
def historique_actions_dispositifs(request):
    """Historique actions dispositifs - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('liste_dispositifs')

@login_required
def ajouter_evenement(request):
    """Ajouter un événement"""
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Vous devez sélectionner un foyer actif pour ajouter un événement.")
        return redirect('mon_profil')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin') or None
        
        if not titre:
            messages.error(request, "Le titre est obligatoire.")
        elif not date_debut:
            messages.error(request, "La date de début est obligatoire.")
        else:
            try:
                # Validation des dates
                from datetime import datetime
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                
                if date_fin:
                    date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                    if date_fin_obj < date_debut_obj:
                        messages.error(request, "La date de fin doit être postérieure ou égale à la date de début.")
                        return render(request, 'maison_app/ajouter_evenement.html', {'foyer': foyer})
                else:
                    date_fin_obj = None
                
                # Créer l'événement
                evenement = Evenement.objects.create(
                    titre=titre,
                    description=description,
                    date_debut=date_debut_obj,
                    date_fin=date_fin_obj,
                    id_foyer=foyer
                )
                
                # Vérifier et débloquer trophée Événement
                verifier_et_debloquer_trophees(request.user, 'evenement', request)
                
                messages.success(request, f"✅ Événement '{titre}' ajouté avec succès !")
                # Rediriger vers le calendrier du mois de l'événement
                return redirect(f'/calendrier/?mois={date_debut_obj.month}&annee={date_debut_obj.year}')
            except ValueError:
                messages.error(request, "Format de date invalide.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de l'événement : {str(e)}")
    
    return render(request, 'maison_app/ajouter_evenement.html', {'foyer': foyer})

@login_required
def modifier_evenement(request, evenement_id):
    """Modifier un événement - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('dashboard')

@login_required
def supprimer_evenement(request, evenement_id):
    """Supprimer un événement - À implémenter"""
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('dashboard')

@login_required
def detail_piece(request, piece_id):
    """Affiche les détails d'une pièce"""
    piece, redirect_response = get_piece_or_redirect(request, piece_id)
    if redirect_response:
        return redirect_response
    
    # Si c'est une cuisine, rediriger vers la vue cuisine
    if piece.type_piece == 'cuisine':
        return redirect('cuisine_view', piece_id=piece.id)
    
    # Récupérer les tâches associées à cette pièce
    taches = Tache.objects.filter(id_piece=piece).order_by('-date_limite')
    taches_actives = taches.filter(terminee=False)
    taches_terminees = taches.filter(terminee=True)
    
    # Récupérer les animaux de cette pièce
    animaux = Animal.objects.filter(id_piece=piece)
    
    return render(request, 'maison_app/detail_piece.html', {
        'piece': piece,
        'taches': taches,
        'taches_actives': taches_actives,
        'taches_terminees': taches_terminees,
        'animaux': animaux
    })

@login_required
def ajouter_budget(request):
    """Ajoute un nouveau budget"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    # Vérifier les permissions
    if not has_permission(request.user, 'can_create_budget'):
        messages.info(request, "Vous devez faire une demande pour créer un budget.")
        return redirect('creer_demande')
    
    if request.method == 'POST':
        categorie_id = request.POST.get('categorie')
        montant_limite = request.POST.get('montant_limite')
        periode = request.POST.get('periode')
        
        try:
            categorie = CategorieDepense.objects.get(id=categorie_id)
            budget = Budget(
                id_foyer=foyer,
                categorie=categorie,
                montant_limite=montant_limite,
                periode=periode
            )
            budget.save()
            # ✅ Vérifier et débloquer trophée Budget
            verifier_et_debloquer_trophees(request.user, 'budget', request)
            messages.success(request, "✅ Budget créé avec succès !")
            return redirect('budget_foyer')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    categories_principales = CategorieDepense.objects.filter(est_categorie_principale=True)
    return render(request, 'maison_app/ajouter_budget.html', {
        'foyer': foyer,
        'categories_principales': categories_principales,
    })

# === API NOTIFICATIONS ===
@login_required
def api_notifications_count(request):
    """API pour obtenir le nombre de notifications non lues"""
    count = request.user.notifications.filter(lue=False).count()
    return JsonResponse({'count': count})

# === MES RÉCOMPENSES ET TROPHÉES ===
@login_required
def mes_recompenses(request):
    """Affiche les récompenses et trophées de l'utilisateur"""
    recompenses = request.user.recompenses.all()
    trophees_debloques = request.user.trophees.filter(debloque=True)
    
    # Récupérer tous les types de trophées possibles
    from .models import Trophee
    tous_types_trophees = [t[0] for t in Trophee.TYPES_TROPHEE]
    
    # Récupérer les types de trophées déjà débloqués
    types_debloques = set(trophees_debloques.values_list('type', flat=True))
    
    # Créer une liste de tous les trophées possibles avec leur statut
    tous_trophees = []
    for type_trophee, nom in Trophee.TYPES_TROPHEE:
        trophee_debloque = trophees_debloques.filter(type=type_trophee).first()
        if trophee_debloque:
            tous_trophees.append({
                'type': type_trophee,
                'nom': trophee_debloque.nom,
                'description': trophee_debloque.description,
                'date_obtention': trophee_debloque.date_obtention,
                'debloque': True
            })
        else:
            # Créer un objet virtuel pour les trophées non débloqués
            nom_trophee = nom.replace(' tâches complétées', '').replace('Streak: ', '').replace('Complété en moins de ', '').replace('Première ', '').replace(' invitations acceptées', '')
            tous_trophees.append({
                'type': type_trophee,
                'nom': nom,
                'description': f"Trophée: {nom}",
                'date_obtention': None,
                'debloque': False
            })
    
    # Séparer les trophées débloqués et non débloqués
    trophees = [t for t in tous_trophees if t['debloque']]
    trophees_non_debloques = [t for t in tous_trophees if not t['debloque']]
    
    # Calculer les points totaux
    total_points = sum(r.points for r in recompenses)
    
    # Historique des points (12 derniers mois)
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Count
    historique_points = []
    for i in range(11, -1, -1):
        mois_debut = timezone.now() - timedelta(days=30*i)
        mois_fin = mois_debut + timedelta(days=30)
        points_mois = recompenses.filter(date_obtention__gte=mois_debut, date_obtention__lt=mois_fin).aggregate(
            total=Sum('points'),
            count=Count('id')
        )
        historique_points.append({
            'mois': mois_debut.strftime('%m/%Y'),
            'nom_mois': mois_debut.strftime('%B %Y'),
            'points': points_mois['total'] or 0,
            'count': points_mois['count'] or 0
        })
    
    # Récompenses avec tâches
    recompenses_avec_taches = recompenses.filter(id_tache__isnull=False).select_related('id_tache')[:10]
    
    return render(request, 'maison_app/mes_recompenses.html', {
        'recompenses': recompenses[:50],  # Limiter à 50 pour la performance
        'trophees': trophees,
        'trophees_non_debloques': trophees_non_debloques,
        'total_points': total_points,
        'historique_points': historique_points,
        'recompenses_avec_taches': recompenses_avec_taches,
    })

# === DEMANDES ===
@login_required
def mes_demandes(request):
    """Affiche les demandes de l'utilisateur"""
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    demandes = Demande.objects.filter(id_user=request.user, id_foyer=foyer).order_by('-date_creation')
    
    return render(request, 'maison_app/mes_demandes.html', {
        'demandes': demandes,
        'foyer': foyer,
    })

@login_required
def creer_demande(request):
    """Crée une nouvelle demande"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    if request.method == 'POST':
        type_demande = request.POST.get('type_demande')
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not titre or not description:
            messages.error(request, "Le titre et la description sont obligatoires.")
            return render(request, 'maison_app/creer_demande.html', {'foyer': foyer})
        
        # Créer la demande
        demande = Demande.objects.create(
            id_user=request.user,
            id_foyer=foyer,
            type_demande=type_demande,
            titre=titre,
            description=description,
            statut='en_attente'
        )
        
        # Notifier tous les admins du foyer (role='admin' ou is_staff)
        admins = foyer.utilisateurs.filter(Q(role='admin') | Q(is_staff=True))
        for admin in admins:
            # Vérifier aussi la permission can_manage_demandes
            if has_permission(admin, 'can_manage_demandes'):
                Notification.objects.create(
                    id_user=admin,
                    type='demande_budget',
                    titre=f"📋 Nouvelle demande: {titre}",
                    message=f"{request.user.nom or request.user.email} a fait une demande: {description[:100]}",
                    id_foyer=foyer
                )
        
        messages.success(request, "✅ Demande créée avec succès ! Les administrateurs ont été notifiés.")
        return redirect('mes_demandes')
    
    return render(request, 'maison_app/creer_demande.html', {'foyer': foyer})

@login_required
def gerer_demandes(request):
    """Gère les demandes (pour les admins)"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    # Vérifier que l'utilisateur est admin
    if not has_permission(request.user, 'can_manage_demandes'):
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent gérer les demandes.")
        return redirect('dashboard')
    
    # Récupérer toutes les demandes en attente du foyer
    demandes_en_attente = Demande.objects.filter(
        id_foyer=foyer,
        statut='en_attente'
    ).order_by('-date_creation')
    
    # Récupérer toutes les demandes traitées
    demandes_traitees = Demande.objects.filter(
        id_foyer=foyer
    ).exclude(statut='en_attente').order_by('-date_traitement')
    
    if request.method == 'POST':
        demande_id = request.POST.get('demande_id')
        action = request.POST.get('action')  # 'accepter' ou 'refuser'
        reponse = request.POST.get('reponse', '').strip()
        
        demande = get_object_or_404(Demande, id=demande_id, id_foyer=foyer)
        
        if action == 'accepter':
            demande.statut = 'acceptee'
            demande.reponse = reponse or "Demande acceptée."
        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.reponse = reponse or "Demande refusée."
        
        demande.date_traitement = timezone.now()
        demande.traite_par = request.user
        demande.save()
        
        # Notifier l'utilisateur qui a fait la demande
        if action == 'accepter':
            titre_notif = f"✅ Demande acceptée: {demande.titre}"
            message_notif = f"Votre demande a été acceptée ! {demande.reponse}"
        else:
            titre_notif = f"❌ Demande refusée: {demande.titre}"
            message_notif = f"Votre demande a été refusée. {demande.reponse}"
        
        Notification.objects.create(
            id_user=demande.id_user,
            type='demande_budget',
            titre=titre_notif,
            message=message_notif,
            id_foyer=foyer
        )
        
        messages.success(request, f"✅ Demande {demande.get_statut_display().lower()} avec succès !")
        return redirect('gerer_demandes')
    
    return render(request, 'maison_app/gerer_demandes.html', {
        'foyer': foyer,
        'demandes_en_attente': demandes_en_attente,
        'demandes_traitees': demandes_traitees,
    })

@login_required
def liste_demandes_foyer(request):
    """Affiche toutes les demandes du foyer (accessible à tous les rôles)"""
    from .permissions import has_permission
    
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
    # Récupérer toutes les demandes du foyer
    toutes_demandes = Demande.objects.filter(id_foyer=foyer).select_related('id_user', 'traite_par').order_by('-date_creation')
    
    # Récupérer les demandes de l'utilisateur actuel
    mes_demandes = toutes_demandes.filter(id_user=request.user)
    mes_demandes_en_cours = mes_demandes.filter(statut='en_attente')
    
    # Pour les admins : permettre de traiter les demandes
    is_admin = has_permission(request.user, 'can_manage_demandes')
    demandes_en_attente = toutes_demandes.filter(statut='en_attente') if is_admin else None
    
    # Traitement des demandes (POST) - uniquement pour les admins
    if request.method == 'POST' and is_admin:
        demande_id = request.POST.get('demande_id')
        action = request.POST.get('action')  # 'accepter' ou 'refuser'
        reponse = request.POST.get('reponse', '').strip()
        
        demande = get_object_or_404(Demande, id=demande_id, id_foyer=foyer)
        
        if action == 'accepter':
            demande.statut = 'acceptee'
            demande.reponse = reponse or "Demande acceptée."
        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.reponse = reponse or "Demande refusée."
        
        demande.date_traitement = timezone.now()
        demande.traite_par = request.user
        demande.save()
        
        # Notifier l'utilisateur qui a fait la demande
        if action == 'accepter':
            titre_notif = f"✅ Demande acceptée: {demande.titre}"
            message_notif = f"Votre demande a été acceptée ! {demande.reponse}"
        else:
            titre_notif = f"❌ Demande refusée: {demande.titre}"
            message_notif = f"Votre demande a été refusée. {demande.reponse}"
        
        Notification.objects.create(
            id_user=demande.id_user,
            type='demande_budget',
            titre=titre_notif,
            message=message_notif,
            id_foyer=foyer
        )
        
        messages.success(request, f"✅ Demande {demande.get_statut_display().lower()} avec succès !")
        return redirect('liste_demandes_foyer')
    
    return render(request, 'maison_app/liste_demandes_foyer.html', {
        'foyer': foyer,
        'toutes_demandes': toutes_demandes,
        'mes_demandes': mes_demandes,
        'mes_demandes_en_cours': mes_demandes_en_cours,
        'demandes_en_attente': demandes_en_attente,
        'is_admin': is_admin,
    })