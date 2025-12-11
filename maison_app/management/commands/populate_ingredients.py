"""
Commande Django pour peupler la base de données avec des ingrédients de base
Usage: python manage.py populate_ingredients
"""
from django.core.management.base import BaseCommand
from maison_app.models import Ingredient


class Command(BaseCommand):
    help = 'Peuple la base de données avec des ingrédients de base'

    def handle(self, *args, **options):
        ingredients_data = [
            # Fruits
            {'nom': 'Pommes', 'categorie': 'Fruits', 'icone': 'bi-apple'},
            {'nom': 'Bananes', 'categorie': 'Fruits', 'icone': 'bi-circle'},
            {'nom': 'Oranges', 'categorie': 'Fruits', 'icone': 'bi-circle'},
            {'nom': 'Fraises', 'categorie': 'Fruits', 'icone': 'bi-circle'},
            {'nom': 'Raisins', 'categorie': 'Fruits', 'icone': 'bi-circle'},
            
            # Légumes
            {'nom': 'Tomates', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Carottes', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Salade', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Oignons', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Ail', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Courgettes', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Aubergines', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            {'nom': 'Poivrons', 'categorie': 'Légumes', 'icone': 'bi-circle'},
            
            # Produits laitiers
            {'nom': 'Lait', 'categorie': 'Produits laitiers', 'icone': 'bi-circle'},
            {'nom': 'Fromage', 'categorie': 'Produits laitiers', 'icone': 'bi-circle'},
            {'nom': 'Beurre', 'categorie': 'Produits laitiers', 'icone': 'bi-circle'},
            {'nom': 'Yaourt', 'categorie': 'Produits laitiers', 'icone': 'bi-circle'},
            {'nom': 'Crème fraîche', 'categorie': 'Produits laitiers', 'icone': 'bi-circle'},
            
            # Viandes & Poissons
            {'nom': 'Poulet', 'categorie': 'Viandes', 'icone': 'bi-circle'},
            {'nom': 'Bœuf', 'categorie': 'Viandes', 'icone': 'bi-circle'},
            {'nom': 'Porc', 'categorie': 'Viandes', 'icone': 'bi-circle'},
            {'nom': 'Saumon', 'categorie': 'Poissons', 'icone': 'bi-circle'},
            {'nom': 'Thon', 'categorie': 'Poissons', 'icone': 'bi-circle'},
            
            # Épicerie
            {'nom': 'Riz', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Pâtes', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Farine', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Sucre', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Huile d\'olive', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Vinaigre', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Sel', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            {'nom': 'Poivre', 'categorie': 'Épicerie', 'icone': 'bi-circle'},
            
            # Boissons
            {'nom': 'Eau', 'categorie': 'Boissons', 'icone': 'bi-cup'},
            {'nom': 'Jus de fruits', 'categorie': 'Boissons', 'icone': 'bi-cup'},
            {'nom': 'Café', 'categorie': 'Boissons', 'icone': 'bi-cup'},
            {'nom': 'Thé', 'categorie': 'Boissons', 'icone': 'bi-cup'},
            
            # Autres
            {'nom': 'Œufs', 'categorie': 'Autres', 'icone': 'bi-circle'},
            {'nom': 'Pain', 'categorie': 'Autres', 'icone': 'bi-circle'},
            {'nom': 'Chocolat', 'categorie': 'Autres', 'icone': 'bi-circle'},
        ]
        
        created_count = 0
        for ing_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                nom=ing_data['nom'],
                defaults={
                    'categorie': ing_data['categorie'],
                    'icone': ing_data['icone']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'OK: {ingredient.nom} cree'))
            else:
                self.stdout.write(self.style.WARNING(f'-> {ingredient.nom} existe deja'))
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} ingredients crees avec succes !'))

