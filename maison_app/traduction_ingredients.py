"""
Dictionnaire de traduction français -> anglais pour les ingrédients courants
"""
TRADUCTION_INGREDIENTS = {
    # Fruits
    'pomme': 'apple', 'pommes': 'apple',
    'banane': 'banana', 'bananes': 'banana',
    'orange': 'orange', 'oranges': 'orange',
    'fraise': 'strawberry', 'fraises': 'strawberry',
    'raisin': 'grape', 'raisins': 'grape',
    
    # Légumes
    'tomate': 'tomato', 'tomates': 'tomato',
    'carotte': 'carrot', 'carottes': 'carrot',
    'salade': 'lettuce',
    'oignon': 'onion', 'oignons': 'onion',
    'ail': 'garlic',
    'courgette': 'zucchini', 'courgettes': 'zucchini',
    'aubergine': 'eggplant', 'aubergines': 'eggplant',
    'poivron': 'bell pepper', 'poivrons': 'bell pepper',
    
    # Produits laitiers
    'lait': 'milk',
    'fromage': 'cheese',
    'beurre': 'butter',
    'yaourt': 'yogurt',
    'crème fraîche': 'sour cream', 'creme fraiche': 'sour cream',
    
    # Viandes
    'poulet': 'chicken',
    'bœuf': 'beef', 'boeuf': 'beef',
    'porc': 'pork',
    'saumon': 'salmon',
    'thon': 'tuna',
    
    # Épicerie
    'riz': 'rice',
    'pâtes': 'pasta', 'pates': 'pasta',
    'farine': 'flour',
    'sucre': 'sugar',
    'huile d\'olive': 'olive oil', 'huile dolive': 'olive oil',
    'vinaigre': 'vinegar',
    'sel': 'salt',
    'poivre': 'pepper',
    
    # Boissons
    'eau': 'water',
    'jus de fruits': 'fruit juice',
    'café': 'coffee', 'cafe': 'coffee',
    'thé': 'tea', 'the': 'tea',
    
    # Autres
    'œuf': 'egg', 'oeuf': 'egg', 'œufs': 'egg', 'oeufs': 'egg',
    'pain': 'bread',
    'chocolat': 'chocolate',
}

def traduire_ingredient(ingredient_fr):
    """
    Traduit un ingrédient français en anglais pour l'API Spoonacular
    
    Args:
        ingredient_fr: Nom de l'ingrédient en français
    
    Returns:
        Nom de l'ingrédient en anglais (ou le nom original si non trouvé)
    """
    ingredient_lower = ingredient_fr.lower().strip()
    
    # Vérifier dans le dictionnaire
    if ingredient_lower in TRADUCTION_INGREDIENTS:
        return TRADUCTION_INGREDIENTS[ingredient_lower]
    
    # Si pas trouvé, retourner le nom original (peut-être déjà en anglais)
    return ingredient_lower

def normaliser_ingredients(ingredients):
    """
    Normalise une liste d'ingrédients (traduction, nettoyage)
    
    Args:
        ingredients: Liste de noms d'ingrédients
    
    Returns:
        Liste d'ingrédients normalisés en anglais
    """
    ingredients_normalises = []
    for ing in ingredients:
        if ing and ing.strip():
            ing_normalise = traduire_ingredient(ing.strip())
            if ing_normalise:
                ingredients_normalises.append(ing_normalise)
    
    return ingredients_normalises

