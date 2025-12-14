#!/usr/bin/env python
"""
Script pour créer les catégories de dépenses par défaut
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_taches_project.settings')
django.setup()

from maison_app.models import CategorieDepense

# Créer les catégories par défaut
categories_data = [
    {'nom': 'Courses', 'couleur': '#28a745', 'icone': 'bi-basket', 'ordre': 1},
    {'nom': 'Restaurants', 'couleur': '#ffc107', 'icone': 'bi-cup-hot', 'ordre': 2},
    {'nom': 'Transport', 'couleur': '#007bff', 'icone': 'bi-car-front', 'ordre': 3},
    {'nom': 'Logement', 'couleur': '#6c757d', 'icone': 'bi-house', 'ordre': 4},
    {'nom': 'Utilities', 'couleur': '#e83e8c', 'icone': 'bi-lightning', 'ordre': 5},
    {'nom': 'Divertissement', 'couleur': '#fd7e14', 'icone': 'bi-film', 'ordre': 6},
    {'nom': 'Santé', 'couleur': '#dc3545', 'icone': 'bi-heart', 'ordre': 7},
    {'nom': 'Vêtements', 'couleur': '#20c997', 'icone': 'bi-bag', 'ordre': 8},
    {'nom': 'Éducation', 'couleur': '#6f42c1', 'icone': 'bi-book', 'ordre': 9},
    {'nom': 'Cadeaux', 'couleur': '#e91e63', 'icone': 'bi-gift', 'ordre': 10},
    {'nom': 'Animaux', 'couleur': '#795548', 'icone': 'bi-heart-pulse', 'ordre': 11},
    {'nom': 'Assurance', 'couleur': '#607d8b', 'icone': 'bi-shield-check', 'ordre': 12},
    {'nom': 'Épargne', 'couleur': '#4caf50', 'icone': 'bi-piggy-bank', 'ordre': 13},
    {'nom': 'Loisirs', 'couleur': '#ff9800', 'icone': 'bi-controller', 'ordre': 14},
    {'nom': 'Beauté & Soins', 'couleur': '#f06292', 'icone': 'bi-flower1', 'ordre': 15},
]

for cat_data in categories_data:
    cat, created = CategorieDepense.objects.get_or_create(
        nom=cat_data['nom'],
        defaults={
            'couleur': cat_data['couleur'],
            'icone': cat_data['icone'],
            'ordre': cat_data['ordre'],
            'est_categorie_principale': True
        }
    )
    if created:
        print(f"✅ Catégorie créée: {cat.nom}")
    else:
        # Mettre à jour les catégories existantes pour s'assurer qu'elles sont principales
        cat.est_categorie_principale = True
        cat.ordre = cat_data['ordre']
        cat.couleur = cat_data['couleur']
        cat.icone = cat_data['icone']
        cat.save()
        print(f"🔄 Catégorie mise à jour: {cat.nom}")

print("✅ Toutes les catégories sont prêtes !")
