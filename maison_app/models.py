from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

# === CHOIX DE RÔLE ===
ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('tresorier', 'Trésorier'),
    ('membre', 'Membre'),
    ('junior', 'Junior'),
    ('invite', 'Invité'),
    ('superviseur', 'Superviseur'),
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
# === INVITATION ===
class Invitation(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    foyer = models.ForeignKey('Foyer', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre')
    cree_par = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    utilise = models.BooleanField(default=False)

    def est_valide(self):
        return not self.utilise and self.date_creation >= timezone.now() - timedelta(days=7)

    class Meta:
        db_table = 'invitation'

    def __str__(self):
        return str(self.code)

# === PIÈCE ===
class Piece(models.Model):
    nom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='pieces/', null=True, blank=True)  # ← PHOTO
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='pieces')  # ← AJOUTÉ

    class Meta:
        db_table = 'piece'

    def __str__(self):
        return self.nom

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

    class Meta:
        db_table = 'tache'

    def __str__(self):
        return self.titre
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

# === LISTE DE COURSES ===
class ListeCourses(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
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

    class Meta:
        db_table = 'aliment'

    def __str__(self):
        return self.nom

# === CHAT MESSAGE ===
class ChatMessage(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE)
    contenu = models.TextField()  # Message + emojis (HTML safe)
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['date_envoi']  # Messages chronologiques

    def __str__(self):
        return f"{self.id_user.email if self.id_user else 'Anonyme'} - {self.date_envoi}"


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
        ('streax', 'Streak: 7 jours consécutifs'),
        ('rapide', 'Complété en moins de 2h'),
        ('premier', 'Première tâche'),
        ('social', '5 invitations acceptées'),
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

# === INVENTAIRE ===
class Inventaire(models.Model):
    nom = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventaire'

    def __str__(self):
        return self.nom

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
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'note'
        ordering = ['-date_modification']

    def __str__(self):
        return self.titre

# === NOTIFICATION ===
class Notification(models.Model):
    TYPES = [
        ('tache_assignee', 'Tâche Assignée'),
        ('tache_complete', 'Tâche Complétée'),
        ('tache_rappel', 'Rappel Tâche'),
        ('budget_alerte', 'Alerte Budget'),
        ('nouveau_membre', 'Nouveau Membre'),
        ('message', 'Message'),
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
    
    class Meta:
        db_table = 'categorie_depense'
    
    def __str__(self):
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
    montant_limite = models.DecimalField(max_digits=10, decimal_places=2)
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