"""
Commande Django pour initialiser les niveaux Snake par défaut
À exécuter une fois pour créer les niveaux de base
"""
from django.core.management.base import BaseCommand
from maison_app.models import NiveauSnake


class Command(BaseCommand):
    help = 'Initialise les niveaux Snake par défaut (niveaux 1 et 2 gratuits, autres à 10 points)'

    def handle(self, *args, **options):
        # Niveaux par défaut
        niveaux = [
            {
                'numero': 1,
                'nom': 'Débutant',
                'description': 'Niveau facile pour apprendre les bases du jeu Snake',
                'vitesse': 150,
                'score_requis': 50,
                'points_deblocage': 0,  # Gratuit
            },
            {
                'numero': 2,
                'nom': 'Intermédiaire',
                'description': 'Niveau moyen avec une vitesse légèrement augmentée',
                'vitesse': 120,
                'score_requis': 100,
                'points_deblocage': 0,  # Gratuit
            },
            {
                'numero': 3,
                'nom': 'Avancé',
                'description': 'Niveau difficile pour les joueurs expérimentés',
                'vitesse': 100,
                'score_requis': 200,
                'points_deblocage': 10,
            },
            {
                'numero': 4,
                'nom': 'Expert',
                'description': 'Niveau très difficile, vitesse rapide',
                'vitesse': 80,
                'score_requis': 300,
                'points_deblocage': 10,
            },
            {
                'numero': 5,
                'nom': 'Maître',
                'description': 'Niveau extrême, pour les vrais champions',
                'vitesse': 60,
                'score_requis': 500,
                'points_deblocage': 10,
            },
        ]
        
        niveaux_crees = 0
        for niveau_data in niveaux:
            niveau, created = NiveauSnake.objects.get_or_create(
                numero=niveau_data['numero'],
                defaults=niveau_data
            )
            if created:
                niveaux_crees += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Niveau {niveau.numero} créé : {niveau.nom}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Niveau {niveau.numero} existe déjà : {niveau.nom}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {niveaux_crees} nouveau(x) niveau(x) créé(s)')
        )

