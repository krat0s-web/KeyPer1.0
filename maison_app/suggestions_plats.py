"""
Suggestions de plats par type de repas pour les menus hebdomadaires
"""
SUGGESTIONS_PLATS = {
    'petit_dejeuner': [
        'Œufs brouillés',
        'Œufs au plat',
        'Œufs à la coque',
        'Omelette',
        'Pancakes',
        'Crêpes',
        'Céréales',
        'Yaourt avec fruits',
        'Pain grillé avec confiture',
        'Pain avec beurre et miel',
        'Fruits frais',
        'Smoothie',
        'Café et croissant',
    ],
    'dejeuner': [
        'Riz au curry',
        'Poulet coréen',
        'Poulet rôti',
        'Pâtes carbonara',
        'Pâtes bolognaise',
        'Pâtes aux légumes',
        'Salade composée',
        'Salade de poulet',
        'Quiche lorraine',
        'Tarte aux légumes',
        'Risotto',
        'Paella',
        'Tajine',
        'Couscous',
        'Burger maison',
        'Pizza maison',
        'Lasagnes',
        'Gratin dauphinois',
        'Ratatouille',
        'Sauté de légumes',
    ],
    'diner': [
        'Soupe de légumes',
        'Soupe à l\'oignon',
        'Salade verte',
        'Salade de pâtes',
        'Omelette aux légumes',
        'Quiche',
        'Tarte salée',
        'Sandwich',
        'Wrap',
        'Salade de riz',
        'Riz sauté',
        'Poulet grillé',
        'Poisson grillé',
        'Légumes grillés',
        'Pâtes aglio e olio',
    ],
    'collation': [
        'Fruits',
        'Yaourt',
        'Compote',
        'Biscuits',
        'Gâteau',
        'Fromage',
        'Noix',
        'Amandes',
        'Barre de céréales',
    ]
}

def get_suggestions_plats(type_repas):
    """Retourne les suggestions de plats pour un type de repas donné"""
    return SUGGESTIONS_PLATS.get(type_repas, [])

