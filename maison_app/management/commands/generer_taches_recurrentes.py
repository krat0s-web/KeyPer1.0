"""
Commande Django pour générer automatiquement les tâches récurrentes
À exécuter via un cron job quotidien
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from maison_app.models import Tache, TacheRecurrente, TacheAssignee, Notification, StatutTache


class Command(BaseCommand):
    help = 'Génère automatiquement les tâches récurrentes selon leur fréquence'

    def handle(self, *args, **options):
        today = timezone.now().date()
        taches_creees = 0
        
        # Récupérer toutes les tâches récurrentes
        taches_recurrentes = TacheRecurrente.objects.select_related('id_tache', 'id_tache__id_foyer').all()
        
        for tache_recurrente in taches_recurrentes:
            tache = tache_recurrente.id_tache
            dernier_execution = tache_recurrente.dernier_execution
            frequence = tache_recurrente.frequence
            
            # Vérifier si une nouvelle tâche doit être créée
            doit_creer = False
            
            if frequence == 'Quotidien':
                # Créer une nouvelle tâche chaque jour
                if dernier_execution is None or dernier_execution < today:
                    doit_creer = True
            elif frequence == 'Hebdo':
                # Créer une nouvelle tâche chaque semaine
                if dernier_execution is None:
                    doit_creer = True
                else:
                    jours_ecoules = (today - dernier_execution).days
                    if jours_ecoules >= 7:
                        doit_creer = True
            elif frequence == 'Mensuel':
                # Créer une nouvelle tâche chaque mois
                if dernier_execution is None:
                    doit_creer = True
                else:
                    # Vérifier si on est dans un nouveau mois
                    if today.year > dernier_execution.year or \
                       (today.year == dernier_execution.year and today.month > dernier_execution.month):
                        doit_creer = True
            
            if doit_creer and not tache.terminee:
                # Créer une nouvelle tâche basée sur la tâche récurrente
                nouvelle_tache = Tache.objects.create(
                    titre=tache.titre,
                    description=tache.description,
                    date_limite=tache.date_limite + timedelta(days=7) if tache.date_limite else None,
                    priorite=tache.priorite,
                    id_statut=tache.id_statut or StatutTache.objects.first(),
                    id_foyer=tache.id_foyer,
                    id_piece=tache.id_piece,
                    id_animal=tache.id_animal,
                    temps_estime=tache.temps_estime,
                    date_rappel=tache.date_rappel + timedelta(days=7) if tache.date_rappel else None,
                    terminee=False
                )
                
                # Copier les assignations de la tâche originale
                assignations_originales = TacheAssignee.objects.filter(id_tache=tache)
                for assignation in assignations_originales:
                    TacheAssignee.objects.create(
                        id_tache=nouvelle_tache,
                        id_user=assignation.id_user,
                        id_piece=assignation.id_piece
                    )
                    # Créer une notification pour l'utilisateur assigné
                    Notification.objects.create(
                        id_user=assignation.id_user,
                        type='tache_assignee',
                        titre=f"📋 Nouvelle tâche récurrente: {nouvelle_tache.titre}",
                        message=f"Une nouvelle occurrence de la tâche récurrente '{nouvelle_tache.titre}' a été créée.",
                        id_tache=nouvelle_tache,
                        id_foyer=nouvelle_tache.id_foyer
                    )
                
                # Mettre à jour la date de dernière exécution
                tache_recurrente.dernier_execution = today
                tache_recurrente.save()
                
                taches_creees += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {taches_creees} tâche(s) récurrente(s) générée(s)')
        )

