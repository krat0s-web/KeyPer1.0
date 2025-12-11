"""
Modèles de données pour l'application KeyPer
=============================================

Ce module contient tous les modèles Django qui représentent les entités
de l'application (Utilisateur, Foyer, Tache, etc.).

Structure :
- Modèles utilisateurs et authentification
- Modèles foyer et gestion de famille
- Modèles tâches et organisation
- Modèles budget et finances
- Modèles chat et communication
- Modèles récompenses et gamification
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator

# === CHOIX DE RÔLE ===
# Définit les rôles disponibles dans l'application
ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('tresorier', 'Trésorier'),
    ('membre', 'Membre'),
    ('junior', 'Junior'),
    ('invite', 'Invité'),
    ('observateur', 'Observateur'),
]

# === MANAGER PERSONNALISÉ ===
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

# === UTILISATEUR ===
class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100, blank=True)  # ← NOM AFFICHÉ
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre')
    foyers = models.ManyToManyField('Foyer', blank=True, related_name='utilisateurs')  # ← PLUSIEURS FOYERS
    foyer_actif = models.ForeignKey('Foyer', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs_actifs')  # ← FOYER ACTUEL
    photo_profil = models.ImageField(upload_to='profiles/', null=True, blank=True)  # ← NOUVELLE PHOTO DE PROFIL
    villes_favorites_meteo = models.JSONField(default=list, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        db_table = 'utilisateur'

    def __str__(self):
        return self.nom or self.email

# === FOYER ===
class Foyer(models.Model):
    nom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='foyers/', null=True, blank=True)  # ← NOUVEAU
    description = models.TextField(blank=True)  # ← NOUVEAU
    cree_par = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='foyers_crees')
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'foyer'

# === INVITATION ===
class Invitation(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    foyer = models.ForeignKey('Foyer', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, blank=True, help_text="Nom optionnel pour identifier l'invitation (ex: 'Invitation famille', 'Invitation1')")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre')
    date_creation = models.DateTimeField(auto_now_add=True)
    utilise = models.BooleanField(default=False)

    def est_valide(self):
        return not self.utilise and self.date_creation >= timezone.now() - timedelta(days=7)

    class Meta:
        db_table = 'invitation'

    def __str__(self):
        if self.nom:
            return f"{self.nom} (code : {self.code})"
        return f"code : {self.code}"

# === TYPES DE PIÈCES PRÉDÉFINIS ===
TYPE_PIECE_CHOICES = [
    ('cuisine', 'Cuisine'),
    ('chambre', 'Chambre'),
    ('toilettes', 'Toilettes'),
    ('salle_de_bain', 'Salle de bain'),
    ('salle_de_jeux', 'Salle de jeux / Loisirs'),
    ('salon', 'Salon'),
    ('buanderie', 'Buanderie / Laverie'),
    ('garage', 'Garage / Atelier'),
    ('jardin', 'Jardin / Extérieur'),
    ('salle_a_manger', 'Salle à manger / Espace commun'),
    ('bureau', 'Bureau'),
    ('personnalise', 'Personnalisé'),
]

# === PIÈCE ===
class Piece(models.Model):
    nom = models.CharField(max_length=100)
    type_piece = models.CharField(max_length=50, choices=TYPE_PIECE_CHOICES, default='personnalise', help_text="Type de pièce prédéfini ou personnalisé")
    description = models.TextField(blank=True, help_text="Description de la fonction de la pièce")
    photo = models.ImageField(upload_to='pieces/', null=True, blank=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='pieces')
    # Permissions d'accès : si vide, tous les membres du foyer peuvent accéder
    utilisateurs_autorises = models.ManyToManyField('Utilisateur', related_name='pieces_autorisees', blank=True, help_text="Utilisateurs autorisés à accéder à cette pièce. Si vide, tous les membres du foyer peuvent y accéder.")

    class Meta:
        db_table = 'piece'

    def __str__(self):
        return self.nom
    
    def get_type_display_name(self):
        """Retourne le nom d'affichage du type de pièce"""
        if self.type_piece == 'personnalise':
            return 'Personnalisé'
        return dict(TYPE_PIECE_CHOICES).get(self.type_piece, self.type_piece)
    
    def peut_acceder(self, utilisateur):
        """Vérifie si un utilisateur peut accéder à cette pièce"""
        # L'admin du foyer a toujours accès
        if utilisateur.role == 'admin' or utilisateur.is_staff:
            return True
        # Si aucun utilisateur spécifique n'est autorisé, tous les membres du foyer ont accès
        if not self.utilisateurs_autorises.exists():
            return utilisateur in self.id_foyer.utilisateurs.all()
        # Sinon, vérifier si l'utilisateur est dans la liste des autorisés
        return self.utilisateurs_autorises.filter(id=utilisateur.id).exists()

class Animal(models.Model):
    nom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='animaux/', null=True, blank=True)  # ← PHOTO
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True, related_name='animaux')  # ← AJOUTÉ
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'animal'

    def __str__(self):
        return self.nom

# === STATUT TÂCHE ===
class StatutTache(models.Model):
    libelle = models.CharField(max_length=50, choices=[
        ('À faire', 'À faire'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Annulée', 'Annulée')
    ])

    class Meta:
        db_table = 'statut_tache'

    def __str__(self):
        return self.libelle

# === TÂCHE ===
class Tache(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_limite = models.DateField(null=True, blank=True)
    priorite = models.CharField(max_length=20, choices=[
        ('Haute', 'Haute'),
        ('Moyenne', 'Moyenne'),
        ('Basse', 'Basse')
    ], null=True, blank=True)
    id_statut = models.ForeignKey(StatutTache, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True, blank=True)
    id_animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True)
    complete_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_completees')
    terminee = models.BooleanField(default=False)
    temps_estime = models.IntegerField(null=True, blank=True, help_text="Temps estimé en minutes")
    date_rappel = models.DateField(null=True, blank=True, help_text="Date de rappel (notification automatique)")

    class Meta:
        db_table = 'tache'

    def __str__(self):
        return self.titre
    
    def has_demande_en_attente(self, user=None):
        """Vérifie si une demande de modification est en attente pour cette tâche"""
        if user:
            return self.demandes_modification.filter(
                id_user=user,
                statut='en_attente'
            ).exists()
        return self.demandes_modification.filter(statut='en_attente').exists()
    
    def has_demande_en_attente_for_user(self, user):
        """Vérifie si l'utilisateur a une demande en attente pour cette tâche"""
        return self.demandes_modification.filter(
            id_user=user,
            statut='en_attente'
        ).exists()
    
    def get_demande_en_attente(self, user=None):
        """Récupère la demande en attente pour cette tâche"""
        if user:
            return self.demandes_modification.filter(
                id_user=user,
                statut='en_attente'
            ).first()
        return self.demandes_modification.filter(statut='en_attente').first()
# === TÂCHE ASSIGNÉE ===
class TacheAssignee(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    date_assignation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tache_assignee'
        unique_together = ('id_tache', 'id_user')

    def __str__(self):
        return f"{self.id_tache.titre} - {self.id_user.email}"

# === TÂCHE RÉCURRENTE ===
class TacheRecurrente(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    frequence = models.CharField(max_length=20, choices=[
        ('Quotidien', 'Quotidien'),
        ('Hebdo', 'Hebdo'),
        ('Mensuel', 'Mensuel')
    ])
    dernier_execution = models.DateField(null=True)

    class Meta:
        db_table = 'tache_recurrente'

    def __str__(self):
        return f"{self.id_tache.titre} - {self.frequence}"

# === JEU SNAKE (SALLE DE JEUX) ===
class NiveauSnake(models.Model):
    """Niveau du jeu Snake"""
    numero = models.IntegerField(unique=True, help_text="Numéro du niveau (1, 2, 3, ...)")
    nom = models.CharField(max_length=100, help_text="Nom du niveau")
    description = models.TextField(blank=True, help_text="Description du niveau")
    vitesse = models.IntegerField(default=100, help_text="Vitesse du serpent (ms entre chaque mouvement)")
    score_requis = models.IntegerField(default=0, help_text="Score requis pour passer au niveau suivant")
    points_deblocage = models.IntegerField(default=0, help_text="Points nécessaires pour débloquer (0 = gratuit)")
    actif = models.BooleanField(default=True, help_text="Si le niveau est actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'niveau_snake'
        ordering = ['numero']
    
    def __str__(self):
        return f"Niveau {self.numero} - {self.nom}"
    
    def est_gratuit(self):
        """Vérifie si le niveau est gratuit (niveaux 1 et 2)"""
        return self.numero <= 2

class NiveauDebloque(models.Model):
    """Niveaux débloqués par utilisateur"""
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='niveaux_snake_debloques')
    id_niveau = models.ForeignKey(NiveauSnake, on_delete=models.CASCADE, related_name='utilisateurs_debloques')
    date_deblocage = models.DateTimeField(auto_now_add=True)
    meilleur_score = models.IntegerField(default=0, help_text="Meilleur score obtenu sur ce niveau")
    date_meilleur_score = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'niveau_debloque'
        unique_together = ('id_user', 'id_niveau')
        ordering = ['-date_deblocage']
    
    def __str__(self):
        return f"{self.id_user.email} - Niveau {self.id_niveau.numero}"
    
    def mettre_a_jour_score(self, nouveau_score):
        """Met à jour le meilleur score si le nouveau est meilleur"""
        if nouveau_score > self.meilleur_score:
            self.meilleur_score = nouveau_score
            self.date_meilleur_score = timezone.now()
            self.save()
            return True
        return False
        return f"Achat pièce {self.numero_piece} - {self.id_user.email} - {self.points_depenses} pts"

# === COMMENTAIRE TÂCHE ===
class CommentaireTache(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='commentaires')
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commentaire_tache'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commentaire sur {self.id_tache.titre} par {self.id_user.email}"

# === LISTE DE COURSES ===
class ListeCourses(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True, blank=True, related_name='listes_courses')
    statut = models.CharField(max_length=20, choices=[
        ('En cours', 'En cours'),
        ('Acheté', 'Acheté')
    ])

    class Meta:
        db_table = 'liste_courses'

    def __str__(self):
        return self.nom

# === ALIMENT ===
class Aliment(models.Model):
    nom = models.CharField(max_length=100)
    id_liste = models.ForeignKey(ListeCourses, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unite = models.CharField(max_length=20, null=True)
    achete = models.BooleanField(default=False, help_text="Indique si l'aliment a été acheté")

    class Meta:
        db_table = 'aliment'

    def __str__(self):
        return self.nom

# === INGRÉDIENT (pour suggestions) ===
class Ingredient(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    categorie = models.CharField(max_length=50, blank=True, help_text="Ex: Fruits, Légumes, Produits laitiers, etc.")
    icone = models.CharField(max_length=50, default='bi-circle', help_text="Icône Bootstrap Icons")
    
    class Meta:
        db_table = 'ingredient'
        ordering = ['categorie', 'nom']

    def __str__(self):
        return self.nom

# === MENU HEBDOMADAIRE ===
class MenuHebdomadaire(models.Model):
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='menus_hebdomadaires')
    semaine_debut = models.DateField(help_text="Date de début de la semaine (lundi)")
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'menu_hebdomadaire'
        unique_together = ['id_foyer', 'semaine_debut']

    def __str__(self):
        return f"Menu semaine du {self.semaine_debut} - {self.id_foyer.nom}"

# === REPAS (pour les menus) ===
class Repas(models.Model):
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    TYPES_REPAS = [
        ('petit_dejeuner', 'Petit-déjeuner'),
        ('dejeuner', 'Déjeuner'),
        ('diner', 'Dîner'),
        ('collation', 'Collation'),
    ]
    
    id_menu = models.ForeignKey(MenuHebdomadaire, on_delete=models.CASCADE, related_name='repas')
    jour = models.CharField(max_length=20, choices=JOURS_SEMAINE)
    type_repas = models.CharField(max_length=20, choices=TYPES_REPAS)
    nom = models.CharField(max_length=200, help_text="Nom du plat ou description")
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'repas'
        ordering = ['jour', 'type_repas']

    def __str__(self):
        return f"{self.get_jour_display()} - {self.get_type_repas_display()}: {self.nom}"

# === MENU SEMAINE (pour les cuisines) ===
class MenuSemaine(models.Model):
    """Menu de la semaine pour une pièce cuisine"""
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='menus_semaine')
    id_piece = models.ForeignKey(Piece, on_delete=models.CASCADE, related_name='menus_semaine', null=True, blank=True)
    semaine_debut = models.DateField(help_text="Date de début de la semaine (lundi)")
    semaine_fin = models.DateField(help_text="Date de fin de la semaine (dimanche)")
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'menu_semaine'
        unique_together = ['id_foyer', 'semaine_debut']
        ordering = ['-semaine_debut']

    def __str__(self):
        return f"Menu semaine du {self.semaine_debut} - {self.id_foyer.nom}"

# === REPAS MENU SEMAINE ===
class RepasMenu(models.Model):
    """Repas pour un menu de la semaine"""
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    TYPES_REPAS = [
        ('petit_dejeuner', 'Petit-déjeuner'),
        ('dejeuner', 'Déjeuner'),
        ('diner', 'Dîner'),
        ('collation', 'Collation'),
    ]
    
    id_menu = models.ForeignKey(MenuSemaine, on_delete=models.CASCADE, related_name='repas')
    jour = models.CharField(max_length=20, choices=JOURS_SEMAINE)
    type_repas = models.CharField(max_length=20, choices=TYPES_REPAS)
    nom = models.CharField(max_length=200, help_text="Nom du plat ou description")
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'repas_menu'
        ordering = ['jour', 'type_repas']

    def __str__(self):
        return f"{self.get_jour_display()} - {self.get_type_repas_display()}: {self.nom}"

# === HISTORIQUE DES RECETTES GÉNÉRÉES ===
class RecetteGeneree(models.Model):
    """Historique des recettes générées par les utilisateurs"""
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='recettes_generees')
    id_piece = models.ForeignKey(Piece, on_delete=models.CASCADE, related_name='recettes_generees', null=True, blank=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='recettes_generees')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Informations de la recette
    titre = models.CharField(max_length=200)
    recette_id_api = models.CharField(max_length=100, help_text="ID de la recette dans l'API (Forkify)")
    image_url = models.URLField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True, help_text="Lien vers la recette originale")
    temps_preparation = models.IntegerField(null=True, blank=True, help_text="Temps de préparation en minutes")
    portions = models.IntegerField(null=True, blank=True)
    
    # Ingrédients utilisés pour la recherche
    ingredients_recherche = models.TextField(help_text="Ingrédients utilisés pour générer cette recette (séparés par des virgules)")
    
    # Détails de la recette (JSON pour stocker les ingrédients complets)
    ingredients_details = models.JSONField(default=list, blank=True, help_text="Liste complète des ingrédients de la recette")
    instructions = models.TextField(blank=True, null=True, help_text="Instructions de préparation de la recette")
    
    class Meta:
        db_table = 'recette_generee'
        ordering = ['-date_creation']
        verbose_name = 'Recette générée'
        verbose_name_plural = 'Recettes générées'

    def __str__(self):
        return f"{self.titre} - {self.date_creation.strftime('%d/%m/%Y')}"

# === CHAT MESSAGE ===
class ChatMessage(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE)
    contenu = models.TextField()  # Message + emojis (HTML safe)
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(null=True, blank=True)  # Date de dernière modification
    est_supprime = models.BooleanField(default=False)  # Indique si le message est supprimé
    est_modifie = models.BooleanField(default=False)  # Indique si le message a été modifié
    fichier = models.FileField(upload_to='chat_files/', null=True, blank=True)  # Fichier (image ou PDF)
    type_fichier = models.CharField(max_length=20, blank=True, choices=[
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('autre', 'Autre')
    ])  # Type de fichier

    class Meta:
        db_table = 'chat_message'
        ordering = ['date_envoi']  # Messages chronologiques

    def __str__(self):
        return f"{self.id_user.email if self.id_user else 'Anonyme'} - {self.date_envoi}"
    
    def est_image(self):
        """Vérifie si le fichier est une image"""
        if self.fichier and self.type_fichier == 'image':
            return True
        return False
    
    def est_pdf(self):
        """Vérifie si le fichier est un PDF"""
        if self.fichier and self.type_fichier == 'pdf':
            return True
        return False


# === RÉCOMPENSE ===
class Recompense(models.Model):
    TYPES = [
        ('points', 'Points'),
        ('badge', 'Badge'),
        ('trophy', 'Trophée'),
    ]
    
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='recompenses')
    type = models.CharField(max_length=20, choices=TYPES, default='points')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=10)
    icone = models.CharField(max_length=50, default='bi-star')  # Bootstrap icon
    date_obtention = models.DateTimeField(auto_now_add=True)
    id_tache = models.ForeignKey('Tache', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'recompense'
        ordering = ['-date_obtention']

    def __str__(self):
        return f"{self.id_user.email} - {self.nom} ({self.points} pts)"

# === TROPHÉE ===
class Trophee(models.Model):
    TYPES_TROPHEE = [
        ('100', '100 tâches complétées'),
        ('50', '50 tâches complétées'),
        ('10', '10 tâches complétées'),
        ('streak', 'Streak: 7 jours consécutifs'),
        ('rapide', 'Complété en moins de 2h'),
        ('premier', 'Première tâche'),
        ('social', '5 invitations acceptées'),
        ('200', '200 tâches complétées'),
        ('500', '500 tâches complétées'),
        ('1000', '1000 tâches complétées'),
        ('streak_30', 'Streak: 30 jours consécutifs'),
        ('streak_100', 'Streak: 100 jours consécutifs'),
        ('efficace', '10 tâches complétées en une journée'),
        ('organise', '50 tâches complétées à l\'avance'),
        ('collaborateur', '20 tâches assignées à d\'autres'),
        ('punctuel', '50 tâches complétées à temps'),
        ('maitre', 'Maître de la maison - 100% des tâches complétées'),
        ('explorateur', 'A visité toutes les pièces'),
        ('budget', 'Gestionnaire de budget - 10 budgets créés'),
        ('animal', 'Ami des animaux - 5 animaux ajoutés'),
        ('note', 'Preneur de notes - 20 notes créées'),
        ('evenement', 'Organisateur - 10 événements créés'),
    ]
    
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='trophees')
    type = models.CharField(max_length=50, choices=TYPES_TROPHEE)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=50)  # Bootstrap icon
    date_obtention = models.DateTimeField(auto_now_add=True)
    debloque = models.BooleanField(default=False)

    class Meta:
        db_table = 'trophee'
        ordering = ['-date_obtention']
        unique_together = ('id_user', 'type')

    def __str__(self):
        return f"{self.id_user.email} - {self.nom}"

# === STATISTIQUE ===
class Statistique(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    nb_taches_done = models.IntegerField(default=0)
    temps_connexion = models.TimeField(null=True)
    date_stat = models.DateField()

    class Meta:
        db_table = 'statistique'

    def __str__(self):
        return f"{self.id_user.email} - {self.date_stat}"


# === TUTO ===
class Tuto(models.Model):
    titre = models.CharField(max_length=100)
    instructions = models.TextField()
    id_tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tuto'

    def __str__(self):
        return self.titre

# === NOUVEAUX CHOIX POUR INVENTAIRE ===
TYPE_ARTICLE_CHOICES = [
    ('aliment', 'Aliment'),
    ('hygiene', 'Hygiène & Entretien'),
    ('autre', 'Autre'),
]

ETAT_ARTICLE_CHOICES = [
    ('disponible', 'Disponible'),
    ('a_court', 'À Court'),  # Indique qu'il faut en racheter
]

# === INVENTAIRE ===
class Inventaire(models.Model):
    nom = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unite = models.CharField(max_length=20, null=True, blank=True, help_text="Unité de mesure (kg, L, pièce, etc.)")
    quantite_alerte_min = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    type_article = models.CharField(max_length=10, choices=TYPE_ARTICLE_CHOICES, default='aliment')
    etat = models.CharField(max_length=10, choices=ETAT_ARTICLE_CHOICES, default='disponible')

    class Meta:
        db_table = 'inventaire'

    def __str__(self):
        return self.nom
    
    def est_en_alerte(self):
        """Si la quantité est inférieure ou égale au seuil défini"""
        return self.quantite <= self.quantite_alerte_min

# === UTILISATION RESSOURCE ===
class UtilisationRessource(models.Model):
    id_inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    quantite_utilisee = models.DecimalField(max_digits=10, decimal_places=2)
    date_utilisation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilisation_ressource'

    def __str__(self):
        return f"{self.id_inventaire.nom} - {self.quantite_utilisee}"

# === ÉVÉNEMENT ===
class Evenement(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField(null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'evenement'

    def __str__(self):
        return self.titre

# === TÂCHE ÉVÉNEMENT ===
class TacheEvenement(models.Model):
    id_evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tache_evenement'

    def __str__(self):
        return f"{self.id_evenement.titre} - {self.id_tache.titre}"

# === DISPOSITIF ===
class Dispositif(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[
        ('capteur', 'Capteur'),
        ('lampe', 'Lampe'),
        ('thermostat', 'Thermostat')
    ])
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    etat = models.BooleanField(default=False)

    class Meta:
        db_table = 'dispositif'

    def __str__(self):
        return self.nom

# === ACTION DISPOSITIF ===
class ActionDispositif(models.Model):
    id_dispositif = models.ForeignKey(Dispositif, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[
        ('allumer', 'Allumer'),
        ('eteindre', 'Éteindre')
    ])
    date_execution = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'action_dispositif'

    def __str__(self):
        return f"{self.id_dispositif.nom} - {self.action}"



# === HISTORIQUE TÂCHE ===
class HistoriqueTache(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_execution = models.DateTimeField(auto_now_add=True)
    duree = models.TimeField(null=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'historique_tache'

    def __str__(self):
        return f"{self.id_tache.titre} - {self.id_user.email}"

# === SUGGESTION TÂCHE ===
class SuggestionTache(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priorite = models.CharField(max_length=20, choices=[
        ('Haute', 'Haute'),
        ('Moyenne', 'Moyenne'),
        ('Basse', 'Basse')
    ], null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    date_suggestion = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('rejetee', 'Rejetée')
    ])

    class Meta:
        db_table = 'suggestion_tache'

    def __str__(self):
        return self.titre

# === PRÉFÉRENCE UTILISATEUR ===
class PreferenceUtilisateur(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    type_tache = models.CharField(max_length=50, choices=[
        ('nettoyage', 'Nettoyage'),
        ('cuisine', 'Cuisine'),
        ('courses', 'Courses'),
        ('entretien', 'Entretien')
    ])
    preference = models.CharField(max_length=20, choices=[
        ('aime', 'Aime'),
        ('desapprouve', 'Désapprouve')
    ])
    disponibilite = models.CharField(max_length=20, choices=[
        ('matin', 'Matin'),
        ('soir', 'Soir'),
        ('jour', 'Jour')
    ])

    class Meta:
        db_table = 'preference_utilisateur'

    def __str__(self):
        return f"{self.id_user.email} - {self.type_tache}"

# === PERMISSIONS PERSONNALISÉES PAR FOYER ===
class PermissionFoyer(models.Model):
    """Permissions personnalisées accordées par un admin à un utilisateur pour un foyer spécifique"""
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='permissions_foyer')
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='permissions_utilisateurs')
    can_access_budget = models.BooleanField(default=False)
    can_create_depense = models.BooleanField(default=False)
    can_delete_depense = models.BooleanField(default=False)
    can_create_budget = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_foyer'
        unique_together = ('id_user', 'id_foyer')
    
    def __str__(self):
        return f"{self.id_user.email} - {self.id_foyer.nom} - Budget: {self.can_access_budget}"
    
    def save(self, *args, **kwargs):
        # Si l'accès au budget est autorisé, donner tous les droits budget automatiquement
        if self.can_access_budget:
            self.can_create_depense = True
            self.can_delete_depense = True
            self.can_create_budget = True
        super().save(*args, **kwargs)

# === INTERACTION IA ===
class InteractionIa(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    commande = models.TextField()
    reponse = models.TextField(blank=True)
    date_interaction = models.DateTimeField(auto_now_add=True)
    id_tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'interaction_ia'

    def __str__(self):
        return f"{self.id_user.email} - {self.date_interaction}"

# === NOTE ===
class Note(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notes')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    couleur_fond = models.CharField(max_length=7, default='#FFF9C4', help_text="Couleur de fond en hexadécimal (ex: #FFF9C4)")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'note'
        ordering = ['-date_modification']

    def __str__(self):
        return self.titre

# === DEMANDE MODIFICATION DATE ===
class DemandeModificationDate(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]
    
    id_tache = models.ForeignKey('Tache', on_delete=models.CASCADE, related_name='demandes_modification')
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes_modification')
    nouvelle_date = models.DateField()
    message = models.TextField(blank=True)  # Champ de texte optionnel
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_traitees')
    
    class Meta:
        db_table = 'demande_modification_date'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Demande pour {self.id_tache.titre} - {self.id_user.email}"

# === DEMANDE (Budget/Accès) ===
class Demande(models.Model):
    TYPES_DEMANDE = [
        ('budget', 'Demande de budget'),
        ('depense', 'Demande de dépense'),
        ('acces_page', 'Demande d\'accès à une page'),
        ('acces_fonctionnalite', 'Demande d\'accès à une fonctionnalité'),
    ]
    
    STATUTS = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]
    
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes')
    id_foyer = models.ForeignKey('Foyer', on_delete=models.CASCADE, related_name='demandes')
    type_demande = models.CharField(max_length=30, choices=TYPES_DEMANDE)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_budget_traitees')
    reponse = models.TextField(blank=True, help_text="Réponse de l'admin")
    
    class Meta:
        db_table = 'demande'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_demande_display()} - {self.titre} - {self.id_user.email}"

# === NOTIFICATION ===
class Notification(models.Model):
    TYPES = [
        ('tache_assignee', 'Tâche Assignée'),
        ('tache_complete', 'Tâche Complétée'),
        ('tache_rappel', 'Rappel Tâche'),
        ('budget_alerte', 'Alerte Budget'),
        ('nouveau_membre', 'Nouveau Membre'),
        ('message', 'Message'),
        ('demande_modification', 'Demande de Modification'),
        ('demande_budget', 'Demande de Budget'),
    ]
    
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    id_tache = models.ForeignKey('Tache', on_delete=models.CASCADE, null=True, blank=True)
    id_foyer = models.ForeignKey('Foyer', on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.id_user.email}"

# === CATÉGORIE DÉPENSE ===
class CategorieDepense(models.Model):
    nom = models.CharField(max_length=100)
    couleur = models.CharField(max_length=7, default='#0d6efd')  # Couleur hex
    icone = models.CharField(max_length=50, default='bi-tag')  # Bootstrap icon
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sous_categories')
    est_categorie_principale = models.BooleanField(default=True)  # True pour catégorie principale, False pour sous-catégorie
    ordre = models.IntegerField(default=0)  # Pour ordonner l'affichage
    
    class Meta:
        db_table = 'categorie_depense'
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} > {self.nom}"
        return self.nom
    
    def get_nom_complet(self):
        """Retourne le nom complet avec la catégorie parente"""
        if self.parent:
            return f"{self.parent.nom} > {self.nom}"
        return self.nom

# === DÉPENSE ===
class Depense(models.Model):
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='depenses')
    description = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.ForeignKey(CategorieDepense, on_delete=models.SET_NULL, null=True, blank=True)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='depenses_creees')
    date_depense = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'depense'
        ordering = ['-date_depense']
    
    def __str__(self):
        return f"{self.description} - {self.montant}€"

# === BUDGET ===
class Budget(models.Model):
    PERIODES = [
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('annuel', 'Annuel'),
    ]
    
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='budgets')
    categorie = models.ForeignKey(CategorieDepense, on_delete=models.CASCADE, null=True, blank=True)
    montant_limite = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    periode = models.CharField(max_length=20, choices=PERIODES, default='mensuel')
    date_debut = models.DateField(auto_now_add=True, null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'budget'
    
    def __str__(self):
        return f"Budget {self.categorie.nom} - {self.montant_limite}€"
    
    def montant_utilise(self):
        """Calcule le montant utilisé selon la période"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if self.periode == 'mensuel':
            date_min = today.replace(day=1)
        elif self.periode == 'trimestriel':
            trimestre = (today.month - 1) // 3
            date_min = today.replace(month=trimestre * 3 + 1, day=1)
        else:  # annuel
            date_min = today.replace(month=1, day=1)
        
        depenses = Depense.objects.filter(
            id_foyer=self.id_foyer,
            categorie=self.categorie,
            date_depense__gte=date_min
        ).aggregate(total=models.Sum('montant'))['total'] or 0
        
        return float(depenses)
    
    def pourcentage_utilise(self):
        """Retourne le pourcentage du budget utilisé"""
        if self.montant_limite == 0:
            return 0
        return round((self.montant_utilise() / float(self.montant_limite)) * 100, 2)
    
    def alerte(self):
        """Retourne si le budget est dépassé ou proche"""
        pourcentage = self.pourcentage_utilise()
        if pourcentage >= 100:
            return 'danger'
        elif pourcentage >= 80:
            return 'warning'
        return 'success'