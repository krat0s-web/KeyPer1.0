"""
Commande Django pour corriger les utilisateurs qui ont des foyers mais pas de foyer actif
"""
from django.core.management.base import BaseCommand
from maison_app.models import Utilisateur


class Command(BaseCommand):
    help = 'Corrige les utilisateurs qui ont des foyers mais pas de foyer actif'

    def handle(self, *args, **options):
        # Trouver tous les utilisateurs qui ont des foyers mais pas de foyer actif
        utilisateurs = Utilisateur.objects.filter(foyers__isnull=False).distinct()
        
        corriges = 0
        for utilisateur in utilisateurs:
            # Recharger pour avoir les foyers à jour
            utilisateur.refresh_from_db()
            
            if utilisateur.foyers.exists():
                if not utilisateur.foyer_actif:
                    utilisateur.foyer_actif = utilisateur.foyers.first()
                    utilisateur.save(update_fields=['foyer_actif'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Foyer actif défini pour {utilisateur.email}: {utilisateur.foyer_actif.nom}'
                        )
                    )
                    corriges += 1
                elif utilisateur.foyer_actif not in utilisateur.foyers.all():
                    utilisateur.foyer_actif = utilisateur.foyers.first()
                    utilisateur.save(update_fields=['foyer_actif'])
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Foyer actif corrigé pour {utilisateur.email}: {utilisateur.foyer_actif.nom}'
                        )
                    )
                    corriges += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {corriges} utilisateur(s) corrigé(s)')
        )









