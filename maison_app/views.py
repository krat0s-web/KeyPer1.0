from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tache, Foyer, Utilisateur, StatutTache, Invitation, Piece, Animal, ChatMessage, Note, Notification, Depense, Budget, CategorieDepense, TacheAssignee, Recompense, Trophee  # ← IMPORTS COMPLETS
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth import logout
from .models import ROLE_CHOICES  # ← AJOUTEZ CET IMPORT
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.http import JsonResponse


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
                next_url = request.GET.get('next', '/taches/')
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
    if request.user.foyer_actif:
        taches = Tache.objects.filter(id_foyer=request.user.foyer_actif).select_related('id_piece', 'id_animal', 'id_statut', 'complete_par')
    else:
        taches = Tache.objects.none()

    return render(request, 'maison_app/liste_taches.html', {
        'taches': taches
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

    # AFFICHE LES FOYERS SELON LE RÔLE
    if request.user.role == 'admin':
        # Les admins voient TOUS les foyers
        foyers = Foyer.objects.prefetch_related('pieces', 'animaux')
    else:
        # Les autres voient uniquement leurs foyers
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
    return render(request, 'maison_app/ajouter_tache.html', {
        'statuts': statuts,
        'pieces': pieces,
        'animaux': animaux,
        'membres': membres,
    })

@login_required
def creer_foyer(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    if request.method == 'POST':
        nom = request.POST['nom']
        description = request.POST.get('description', '')
        photo = request.FILES.get('photo')
        
        foyer = Foyer(nom=nom, description=description)
        if photo:
            foyer.photo = photo
        foyer.save()

        # Associe l'admin au foyer
        request.user.foyers.add(foyer)
        request.user.foyer_actif = foyer
        request.user.save()

        messages.success(request, f"Foyer '{nom}' créé !")
        return redirect('liste_foyers')
    
    return render(request, 'maison_app/creer_foyer.html')

@login_required
def ajouter_piece(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter une pièce.")
        return redirect('liste_foyers')

    if not request.user.foyer_actif:
        messages.error(request, "Vous devez d'abord créer un foyer.")
        return redirect('creer_foyer')

    if request.method == 'POST':
        nom = request.POST['nom']
        photo = request.FILES.get('photo')
        
        piece = Piece(nom=nom, id_foyer=request.user.foyer_actif)
        if photo:
            piece.photo = photo
        piece.save()
        messages.success(request, f"Pièce '{nom}' ajoutée !")
        return redirect('liste_foyers')

    return render(request, 'maison_app/ajouter_piece.html')

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
        messages.success(request, f"Animal '{nom}' ajouté !")
        return redirect('liste_foyers')

    pieces = Piece.objects.filter(id_foyer=request.user.foyer_actif)
    return render(request, 'maison_app/ajouter_animal.html', {'pieces': pieces})

@login_required
def supprimer_piece(request, piece_id):
    piece = get_object_or_404(Piece, id=piece_id)
    
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer une pièce.")
        return redirect('detail_foyer', foyer_id=piece.id_foyer.id)
    
    # Vérifier que l'utilisateur a accès à ce foyer
    if piece.id_foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
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
    
    # Récupérer l'invitation actuelle (non utilisée)
    invitation_actuelle = Invitation.objects.filter(foyer=foyer, utilise=False).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'regenerer':
            # Supprimer l'ancienne invitation et en créer une nouvelle
            if invitation_actuelle:
                invitation_actuelle.delete()
            
            role = request.POST.get('role', 'membre')
            invitation = Invitation.objects.create(
                foyer=foyer,
                role=role,
                cree_par=request.user
            )
            messages.success(request, f"Nouveau code d'invitation généré : {invitation.code}")
        else:
            # Créer nouvelle invitation
            role = request.POST.get('role', 'membre')
            invitation = Invitation.objects.create(
                foyer=foyer,
                role=role,
                cree_par=request.user
            )
            messages.success(request, f"Code d'invitation : {invitation.code}")
        
        return redirect('generer_invitation', foyer_id=foyer_id)

    # Actualiser l'invitation actuelle après POST
    invitation_actuelle = Invitation.objects.filter(foyer=foyer, utilise=False).first()

    return render(request, 'maison_app/generer_invitation.html', {
        'foyer': foyer,
        'invitation_actuelle': invitation_actuelle,
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


def rejoindre_foyer(request):
    if request.method == 'POST':
        code = request.POST['code']
        
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
                    request.user.role = invitation.role
                    request.user.save()

                    invitation.utilise = True
                    invitation.save()
                    
                    # ✅ Créer une notification pour tous les autres membres
                    foyer = invitation.foyer
                    for utilisateur in foyer.utilisateurs.all():
                        if utilisateur != request.user:
                            Notification.objects.create(
                                id_user=utilisateur,
                                type='nouveau_membre',
                                titre=f"👥 Nouveau membre: {request.user.nom or request.user.email}",
                                message=f"{request.user.nom or request.user.email} a rejoint le foyer {foyer.nom}",
                                id_foyer=foyer
                            )

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

                    messages.success(request, f"Bienvenue {nom} dans le foyer {invitation.foyer.nom} !")
                    login(request, utilisateur)  # Connexion automatique
                    return redirect('liste_taches')
            else:
                messages.error(request, "Code expiré ou déjà utilisé.")
        except Invitation.DoesNotExist:
            messages.error(request, "Code invalide.")
    
    return render(request, 'maison_app/rejoindre.html')

@login_required
def terminer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.foyer_actif)
    if tache.terminee:
        messages.error(request, "Tâche déjà terminée.")
        return redirect('detail_foyer', foyer_id=tache.id_foyer.id)

    tache.terminee = True
    tache.complete_par = request.user
    tache.save()
    
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
    
    # ✅ Vérifier et créer des trophées
    nb_taches_completes = Tache.objects.filter(
        id_foyer=tache.id_foyer,
        complete_par=request.user,
        terminee=True
    ).count()
    
    if nb_taches_completes == 1:
        # Premier trophée
        Trophee.objects.get_or_create(
            id_user=request.user,
            type='premier',
            defaults={
                'nom': '🏅 Première Tâche',
                'description': 'Vous avez complété votre première tâche',
                'icone': 'bi-trophy',
                'debloque': True
            }
        )
    elif nb_taches_completes == 10:
        Trophee.objects.get_or_create(
            id_user=request.user,
            type='10',
            defaults={
                'nom': '🏆 10 Tâches',
                'description': 'Vous avez complété 10 tâches',
                'icone': 'bi-stars',
                'debloque': True
            }
        )
    elif nb_taches_completes == 50:
        Trophee.objects.get_or_create(
            id_user=request.user,
            type='50',
            defaults={
                'nom': '⭐ 50 Tâches',
                'description': 'Vous avez complété 50 tâches',
                'icone': 'bi-star-fill',
                'debloque': True
            }
        )
    elif nb_taches_completes == 100:
        Trophee.objects.get_or_create(
            id_user=request.user,
            type='100',
            defaults={
                'nom': '👑 100 Tâches',
                'description': 'Vous avez complété 100 tâches',
                'icone': 'bi-gem',
                'debloque': True
            }
        )
    
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
# === INSCRIPTION (NOUVELLE PAGE) ===
def inscription(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'registration/inscription.html')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'registration/inscription.html')

        user = Utilisateur.objects.create_user(
            email=email,
            username=email,
            nom=nom,
            password=password,
            role='membre'
        )
        login(request, user)
        messages.success(request, f"Bienvenue {nom} ! Votre compte est créé.")
        return redirect('liste_taches')

    return render(request, 'registration/inscription.html')

# === MES NOTES ===
@login_required
def mes_notes(request):
    if request.method == 'POST':
        if 'ajouter' in request.POST:
            titre = request.POST.get('titre', '')
            contenu = request.POST.get('contenu', '')
            if titre and contenu:
                Note.objects.create(id_user=request.user, titre=titre, contenu=contenu)
                messages.success(request, "Note ajoutée !")
            else:
                messages.error(request, "Titre et contenu requis.")
            return redirect('mes_notes')
        
        elif 'modifier' in request.POST:
            note_id = request.POST.get('note_id')
            titre = request.POST.get('titre', '')
            contenu = request.POST.get('contenu', '')
            note = get_object_or_404(Note, id=note_id, id_user=request.user)
            note.titre = titre
            note.contenu = contenu
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
        if 'modifier_infos' in request.POST:
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
    
    # Récupérer tous les foyers de l'utilisateur
    foyers = request.user.foyers.all()
    
    return render(request, 'maison_app/mon_profil.html', {
        'foyers': foyers,
        'foyer_actuel': request.user.foyer_actif
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
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
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
    
    return render(request, 'maison_app/budget_foyer.html', {
        'foyer': foyer,
        'budgets_data': budgets_data,
        'depenses_recentes': depenses_recentes,
        'total_depenses': total_depenses,
        'total_budget': total_budget,
    })

@login_required
def ajouter_depense(request):
    """Ajoute une nouvelle dépense"""
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
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
    
    categories = CategorieDepense.objects.all()
    return render(request, 'maison_app/ajouter_depense.html', {
        'foyer': foyer,
        'categories': categories,
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
def ajouter_budget(request):
    """Ajoute un nouveau budget"""
    foyer = request.user.foyer_actif
    if not foyer:
        messages.error(request, "Aucun foyer actif sélectionné.")
        return redirect('liste_foyers')
    
    if foyer not in request.user.foyers.all():
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')
    
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
            messages.success(request, "✅ Budget créé avec succès !")
            return redirect('budget_foyer')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    categories = CategorieDepense.objects.all()
    return render(request, 'maison_app/ajouter_budget.html', {
        'foyer': foyer,
        'categories': categories,
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
    trophees = request.user.trophees.filter(debloque=True)
    
    # Calculer les points totaux
    total_points = sum(r.points for r in recompenses)
    
    return render(request, 'maison_app/mes_recompenses.html', {
        'recompenses': recompenses,
        'trophees': trophees,
        'total_points': total_points,
    })