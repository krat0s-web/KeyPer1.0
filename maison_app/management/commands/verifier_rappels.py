"""
Commande Django pour vérifier et envoyer les rappels automatiques des tâches
À exécuter via un cron job quotidien
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from maison_app.models import Tache, Notification


class Command(BaseCommand):
    help = 'Vérifie les tâches avec rappels et crée des notifications'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Trouver les tâches avec date_rappel aujourd'hui ou demain
        taches_rappel = Tache.objects.filter(
            date_rappel__lte=tomorrow,
            date_rappel__gte=today,
            terminee=False
        ).select_related('id_foyer', 'complete_par')
        
        notifications_creees = 0
        
        for tache in taches_rappel:
            # Vérifier si une notification a déjà été créée pour ce rappel
            notification_existante = Notification.objects.filter(
                id_tache=tache,
                type='rappel',
                date_creation__date=today
            ).exists()
            
            if not notification_existante:
                # Créer une notification pour tous les membres du foyer
                if tache.id_foyer:
                    for utilisateur in tache.id_foyer.utilisateurs.all():
                        # Ne pas notifier si la tâche est déjà terminée
                        if not tache.terminee:
                            jours_restants = (tache.date_rappel - today).days
                            if jours_restants == 0:
                                message = f"Rappel : La tâche '{tache.titre}' est prévue pour aujourd'hui !"
                            elif jours_restants == 1:
                                message = f"Rappel : La tâche '{tache.titre}' est prévue pour demain !"
                            else:
                                message = f"Rappel : La tâche '{tache.titre}' est prévue dans {jours_restants} jours."
                            
                            Notification.objects.create(
                                id_user=utilisateur,
                                type='rappel',
                                titre=f"🔔 Rappel : {tache.titre}",
                                message=message,
                                id_tache=tache,
                                id_foyer=tache.id_foyer
                            )
                            notifications_creees += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {notifications_creees} notification(s) de rappel créée(s)')
        )









