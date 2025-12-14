from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Foyer, Utilisateur, Piece, Animal, StatutTache, Tache,
    TacheAssignee, TacheRecurrente, ListeCourses, Aliment,
    ChatMessage, Recompense, Statistique, Tuto, Inventaire,
    UtilisationRessource, Evenement, TacheEvenement, Dispositif,
    ActionDispositif, HistoriqueTache,
    SuggestionTache, PreferenceUtilisateur, InteractionIa, Invitation,
    Note, Notification, CategorieDepense, Depense, Budget, Trophee,
    DemandeModificationDate, Ingredient, MenuHebdomadaire, Repas,
    NiveauSnake, NiveauDebloque
)

# === UTILISATEUR (personnalisé) ===
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'foyer_actif', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('email', 'username')
    filter_horizontal = ('foyers',)  # Permet de gérer les foyers dans l'admin
    fieldsets = UserAdmin.fieldsets + (
        ('Informations KeyPer', {
            'fields': ('nom', 'role', 'foyers', 'foyer_actif', 'photo_profil')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Surcharge pour gérer automatiquement le foyer actif
        Le signal m2m_changed gère automatiquement le foyer actif quand les foyers sont modifiés,
        mais on vérifie aussi ici au cas où le foyer_actif est modifié directement
        """
        # Sauvegarder d'abord l'utilisateur
        super().save_model(request, obj, form, change)
        
        # Recharger l'utilisateur pour avoir les foyers à jour
        obj.refresh_from_db()
        
        # Si l'utilisateur a des foyers mais pas de foyer actif, définir le premier comme actif
        if obj.foyers.exists() and not obj.foyer_actif:
            obj.foyer_actif = obj.foyers.first()
            obj.save(update_fields=['foyer_actif'])
        # Vérifier que le foyer actif est bien dans la liste des foyers de l'utilisateur
        elif obj.foyer_actif and obj.foyer_actif not in obj.foyers.all():
            # Si le foyer actif n'est plus dans la liste, définir le premier disponible
            if obj.foyers.exists():
                obj.foyer_actif = obj.foyers.first()
                obj.save(update_fields=['foyer_actif'])
            else:
                obj.foyer_actif = None
                obj.save(update_fields=['foyer_actif'])

# === FOYER (amélioré avec association automatique) ===
@admin.register(Foyer)
class FoyerAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nb_utilisateurs', 'nb_pieces', 'nb_animaux', 'date_creation_display')
    list_filter = ('nom',)
    search_fields = ('nom', 'description')
    readonly_fields = ('nb_utilisateurs', 'nb_pieces', 'nb_animaux', 'liste_utilisateurs', 'date_creation_display')
    
    fieldsets = (
        ('Informations', {
            'fields': ('nom', 'photo', 'description')
        }),
        ('Membres', {
            'fields': ('liste_utilisateurs', 'nb_utilisateurs'),
            'description': 'Pour ajouter un utilisateur à ce foyer, modifiez l\'utilisateur et ajoutez ce foyer dans "Foyers".'
        }),
        ('Statistiques', {
            'fields': ('nb_pieces', 'nb_animaux', 'date_creation_display'),
            'classes': ('collapse',)
        }),
    )
    
    def nb_utilisateurs(self, obj):
        return obj.utilisateurs.count()
    nb_utilisateurs.short_description = "Nombre d'utilisateurs"
    
    def nb_pieces(self, obj):
        return obj.pieces.count()
    nb_pieces.short_description = "Nombre de pièces"
    
    def nb_animaux(self, obj):
        return obj.animaux.count()
    nb_animaux.short_description = "Nombre d'animaux"
    
    def liste_utilisateurs(self, obj):
        utilisateurs = obj.utilisateurs.all()
        if utilisateurs:
            liste = ', '.join([f"{u.nom or u.email}" for u in utilisateurs[:5]])
            if utilisateurs.count() > 5:
                liste += f" ... et {utilisateurs.count() - 5} autre(s)"
            return format_html('<strong>{}</strong>', liste)
        return "Aucun utilisateur"
    liste_utilisateurs.short_description = "Utilisateurs du foyer"
    
    def date_creation_display(self, obj):
        # Utiliser l'ID comme approximation de la date de création
        if obj.id:
            return f"ID: {obj.id}"
        return "-"
    date_creation_display.short_description = "Informations"
    
    def save_model(self, request, obj, form, change):
        """
        Surcharge pour associer automatiquement le foyer à l'utilisateur connecté
        si c'est une nouvelle création et que l'utilisateur est un superuser/admin
        """
        # Sauvegarder d'abord le foyer
        super().save_model(request, obj, form, change)
        
        # Si c'est une nouvelle création (pas une modification)
        if not change:
            # Vérifier si l'utilisateur connecté est un superuser Django
            if request.user.is_superuser:
                # Chercher l'utilisateur correspondant dans le modèle Utilisateur
                try:
                    utilisateur = Utilisateur.objects.get(email=request.user.email)
                    # Associer le foyer à l'utilisateur
                    utilisateur.foyers.add(obj)
                    # Si l'utilisateur n'a pas de foyer actif, définir celui-ci
                    if not utilisateur.foyer_actif:
                        utilisateur.foyer_actif = obj
                        utilisateur.save()
                except Utilisateur.DoesNotExist:
                    # Si l'utilisateur n'existe pas dans le modèle Utilisateur,
                    # c'est un superuser Django qui n'a pas de compte Utilisateur
                    # On ne fait rien dans ce cas
                    pass

# === PIÈCE (UNE SEULE FOIS) ===
@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'id_foyer')
    list_filter = ('id_foyer',)
    search_fields = ('nom',)
# === ANIMAL ===
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nom', 'id_foyer')
    list_filter = ('id_foyer',)
    search_fields = ('nom',)

# === STATUT TÂCHE ===
@admin.register(StatutTache)
class StatutTacheAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    search_fields = ('libelle',)

# === TÂCHE ===
@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):
    list_display = ('titre', 'id_foyer', 'priorite', 'terminee', 'date_limite', 'complete_par')
    list_filter = ('terminee', 'priorite', 'id_foyer', 'id_statut')
    search_fields = ('titre', 'description')
    readonly_fields = ('complete_par', 'terminee')
    date_hierarchy = 'date_limite'
    raw_id_fields = ('id_foyer', 'id_piece', 'id_animal', 'complete_par')

# === TÂCHE ASSIGNÉE ===
@admin.register(TacheAssignee)
class TacheAssigneeAdmin(admin.ModelAdmin):
    list_display = ('id_tache', 'id_user', 'date_assignation')
    list_filter = ('date_assignation',)
    search_fields = ('id_tache__titre', 'id_user__email')
    raw_id_fields = ('id_tache', 'id_user')

# === TÂCHE RÉCURRENTE ===
@admin.register(TacheRecurrente)
class TacheRecurrenteAdmin(admin.ModelAdmin):
    list_display = ('id_tache', 'frequence', 'dernier_execution')
    list_filter = ('frequence',)
    search_fields = ('id_tache__titre',)
    raw_id_fields = ('id_tache',)

# === LISTE DE COURSES ===
@admin.register(ListeCourses)
class ListeCoursesAdmin(admin.ModelAdmin):
    list_display = ('nom', 'id_foyer', 'date_creation')
    list_filter = ('id_foyer', 'date_creation')
    search_fields = ('nom',)
    date_hierarchy = 'date_creation'

# === ALIMENT ===
@admin.register(Aliment)
class AlimentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'achete')
    list_filter = ('achete',)
    search_fields = ('nom',)

# === CHAT MESSAGE ===
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'id_foyer', 'date_envoi', 'est_modifie', 'est_supprime')
    list_filter = ('date_envoi', 'est_modifie', 'est_supprime', 'id_foyer')
    search_fields = ('contenu', 'id_user__email')
    readonly_fields = ('date_envoi', 'date_modification')
    date_hierarchy = 'date_envoi'

# === RÉCOMPENSE ===
@admin.register(Recompense)
class RecompenseAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'type', 'nom', 'points', 'date_obtention')
    list_filter = ('type', 'date_obtention')
    search_fields = ('nom', 'id_user__email')
    date_hierarchy = 'date_obtention'

# === STATISTIQUE ===
@admin.register(Statistique)
class StatistiqueAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'date_stat', 'nb_taches_done', 'temps_connexion')
    list_filter = ('date_stat',)
    search_fields = ('id_user__email',)
    date_hierarchy = 'date_stat'

# === TROPHÉE ===
@admin.register(Trophee)
class TropheeAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'nom', 'type', 'debloque', 'date_obtention')
    list_filter = ('type', 'debloque', 'date_obtention')
    search_fields = ('nom', 'id_user__email')
    readonly_fields = ('date_obtention',)

# === BUDGET ===
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id_foyer', 'categorie', 'montant_limite', 'periode', 'actif')
    list_filter = ('periode', 'actif', 'id_foyer')
    search_fields = ('categorie__nom',)

# === DÉPENSE ===
@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'montant', 'categorie', 'id_foyer', 'date_depense')
    list_filter = ('categorie', 'date_depense', 'id_foyer')
    search_fields = ('description',)
    date_hierarchy = 'date_depense'

# === NOTIFICATION ===
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'type', 'titre', 'lue', 'date_creation')
    list_filter = ('type', 'lue', 'date_creation')
    search_fields = ('titre', 'message', 'id_user__email')
    readonly_fields = ('date_creation',)
    date_hierarchy = 'date_creation'

# === HISTORIQUE TÂCHE ===
@admin.register(HistoriqueTache)
class HistoriqueTacheAdmin(admin.ModelAdmin):
    list_display = ('id_tache', 'id_user', 'date_execution', 'duree')
    list_filter = ('date_execution',)
    search_fields = ('id_tache__titre', 'id_user__email')
    date_hierarchy = 'date_execution'

# === AUTRES MODÈLES ===
admin.site.register(Tuto)
admin.site.register(Inventaire)
admin.site.register(UtilisationRessource)
admin.site.register(Evenement)
admin.site.register(TacheEvenement)
admin.site.register(Dispositif)
admin.site.register(ActionDispositif)
admin.site.register(SuggestionTache)
admin.site.register(PreferenceUtilisateur)
admin.site.register(InteractionIa)
admin.site.register(Invitation)
admin.site.register(Note)
admin.site.register(CategorieDepense)
admin.site.register(DemandeModificationDate)
admin.site.register(Ingredient)
admin.site.register(MenuHebdomadaire)
admin.site.register(Repas)

# === JEU SNAKE ===
@admin.register(NiveauSnake)
class NiveauSnakeAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nom', 'vitesse', 'score_requis', 'points_deblocage', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom', 'description')
    ordering = ['numero']

@admin.register(NiveauDebloque)
class NiveauDebloqueAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'id_niveau', 'meilleur_score', 'date_deblocage', 'date_meilleur_score')
    list_filter = ('date_deblocage', 'id_niveau')
    search_fields = ('id_user__email', 'id_niveau__nom')
    readonly_fields = ('date_deblocage', 'date_meilleur_score')
    date_hierarchy = 'date_deblocage'