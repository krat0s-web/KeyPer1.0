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
    {'nom': 'Courses', 'couleur': '#28a745', 'icone': 'bi-basket'},
    {'nom': 'Restaurants', 'couleur': '#ffc107', 'icone': 'bi-cup-hot'},
    {'nom': 'Transport', 'couleur': '#007bff', 'icone': 'bi-car-front'},
    {'nom': 'Logement', 'couleur': '#6c757d', 'icone': 'bi-house'},
    {'nom': 'Utilities', 'couleur': '#e83e8c', 'icone': 'bi-lightning'},
    {'nom': 'Divertissement', 'couleur': '#fd7e14', 'icone': 'bi-film'},
    {'nom': 'Santé', 'couleur': '#dc3545', 'icone': 'bi-heart'},
    {'nom': 'Vêtements', 'couleur': '#20c997', 'icone': 'bi-bag'},
]

for cat_data in categories_data:
    if not CategorieDepense.objects.filter(nom=cat_data['nom']).exists():
        cat = CategorieDepense.objects.create(**cat_data)
        print(f"✅ Catégorie créée: {cat.nom}")
    else:
        print(f"⏭️ Catégorie existante: {cat_data['nom']}")

print("✅ Toutes les catégories sont prêtes !")
