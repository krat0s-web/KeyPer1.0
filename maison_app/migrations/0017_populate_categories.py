# Generated migration to populate categories and subcategories

from django.db import migrations

def populate_categories(apps, schema_editor):
    CategorieDepense = apps.get_model('maison_app', 'CategorieDepense')
    
    # Liste des catégories principales avec leurs sous-catégories
    categories_data = [
        {
            'nom': '🏠 Maison & Charges',
            'icone': 'bi-house',
            'couleur': '#8B4513',
            'ordre': 1,
            'sous_categories': [
                'Loyer / Crédit immobilier',
                'Électricité',
                'Eau',
                'Gaz',
                'Internet / Téléphone',
                'Assurance habitation',
            ]
        },
        {
            'nom': '🍽️ Alimentation',
            'icone': 'bi-cart',
            'couleur': '#FF6347',
            'ordre': 2,
            'sous_categories': [
                'Courses',
                'Restaurants',
                'Snacking',
            ]
        },
        {
            'nom': '🚗 Transport',
            'icone': 'bi-car-front',
            'couleur': '#4169E1',
            'ordre': 3,
            'sous_categories': [
                'Carburant',
                'Assurance voiture',
                'Réparations / entretien',
                'Transport en commun',
                'Location de véhicules',
            ]
        },
        {
            'nom': '👟 Vie quotidienne',
            'icone': 'bi-person',
            'couleur': '#32CD32',
            'ordre': 4,
            'sous_categories': [
                'Hygiène',
                'Vêtements',
                'Électroménager',
                'Fournitures diverses',
            ]
        },
        {
            'nom': '🎉 Loisirs',
            'icone': 'bi-emoji-smile',
            'couleur': '#FF69B4',
            'ordre': 5,
            'sous_categories': [
                'Cinéma / sorties',
                'Voyages',
                'Abonnements (Netflix, Spotify…)',
                'Sport / salle de sport',
            ]
        },
        {
            'nom': '🩺 Santé',
            'icone': 'bi-heart-pulse',
            'couleur': '#DC143C',
            'ordre': 6,
            'sous_categories': [
                'Rendez-vous médicaux',
                'Pharmacie',
                'Assurance santé',
            ]
        },
        {
            'nom': '👶 Enfants & Famille',
            'icone': 'bi-people',
            'couleur': '#FFD700',
            'ordre': 7,
            'sous_categories': [
                'Garde',
                'École',
                'Activités extrascolaires',
                'Jouets / vêtements enfants',
            ]
        },
        {
            'nom': '💼 Travail / Études',
            'icone': 'bi-briefcase',
            'couleur': '#4682B4',
            'ordre': 8,
            'sous_categories': [
                'Matériel',
                'Frais d\'inscription',
                'Abonnements pro',
                'Livres / logiciels',
            ]
        },
        {
            'nom': '🎁 Cadeaux & Événements',
            'icone': 'bi-gift',
            'couleur': '#FF1493',
            'ordre': 9,
            'sous_categories': [
                'Anniversaires',
                'Mariages',
                'Fêtes',
            ]
        },
        {
            'nom': '⚠️ Urgences & imprévus',
            'icone': 'bi-exclamation-triangle',
            'couleur': '#FF4500',
            'ordre': 10,
            'sous_categories': [
                'Réparations urgentes',
                'Dépannage',
            ]
        },
        {
            'nom': '📈 Épargne & Investissements',
            'icone': 'bi-graph-up',
            'couleur': '#228B22',
            'ordre': 11,
            'sous_categories': [
                'Épargne classique',
                'Investissements',
                'Fonds d\'urgence',
            ]
        },
        {
            'nom': '💳 Dettes & Remboursements',
            'icone': 'bi-credit-card',
            'couleur': '#8B0000',
            'ordre': 12,
            'sous_categories': [
                'Crédits',
                'Remboursements entre proches',
            ]
        },
        {
            'nom': '🛠️ Maison & bricolage',
            'icone': 'bi-tools',
            'couleur': '#696969',
            'ordre': 13,
            'sous_categories': [
                'Travaux',
                'Décoration',
                'Jardin',
            ]
        },
        {
            'nom': '🐶 Animaux',
            'icone': 'bi-heart',
            'couleur': '#FF69B4',
            'ordre': 14,
            'sous_categories': [
                'Nourriture',
                'Vétérinaire',
                'Accessoires',
            ]
        },
        {
            'nom': 'Autres',
            'icone': 'bi-three-dots',
            'couleur': '#808080',
            'ordre': 99,
            'sous_categories': []
        },
    ]
    
    # Créer les catégories principales
    for cat_data in categories_data:
        categorie, created = CategorieDepense.objects.get_or_create(
            nom=cat_data['nom'],
            defaults={
                'icone': cat_data['icone'],
                'couleur': cat_data['couleur'],
                'ordre': cat_data['ordre'],
                'est_categorie_principale': True,
                'parent': None,
            }
        )
        
        # Créer les sous-catégories
        for sous_cat_nom in cat_data['sous_categories']:
            CategorieDepense.objects.get_or_create(
                nom=sous_cat_nom,
                parent=categorie,
                defaults={
                    'icone': 'bi-tag',
                    'couleur': cat_data['couleur'],
                    'ordre': 0,
                    'est_categorie_principale': False,
                }
            )

def reverse_populate_categories(apps, schema_editor):
    CategorieDepense = apps.get_model('maison_app', 'CategorieDepense')
    CategorieDepense.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('maison_app', '0016_add_categories_sous_categories'),
    ]

    operations = [
        migrations.RunPython(populate_categories, reverse_populate_categories),
    ]

