"""
Module pour interagir avec l'API Forkify
Documentation: https://forkify-api.herokuapp.com
"""
import requests

FORKIFY_API_KEY = '596cc11c-d276-478b-9a61-7fb547bcede0'
FORKIFY_BASE_URL = 'https://forkify-api.herokuapp.com/api/v2'

def rechercher_recettes_par_ingredients(ingredients, nombre_recettes=10):
    """
    Recherche des recettes basées sur une liste d'ingrédients
    
    Args:
        ingredients: Liste de noms d'ingrédients (ex: ['tomato', 'chicken', 'onion'])
        nombre_recettes: Nombre de recettes à retourner (par défaut 10)
    
    Returns:
        Liste de dictionnaires contenant les informations des recettes
    """
    try:
        # Convertir la liste d'ingrédients en chaîne pour la recherche
        ingredients_clean = [ing.strip().lower() for ing in ingredients if ing and ing.strip()]
        
        if not ingredients_clean:
            print("Aucun ingrédient valide fourni")
            return []
        
        # Forkify utilise un paramètre 'search' avec les ingrédients séparés par des espaces
        query = ' '.join(ingredients_clean[:5])  # Utiliser les 5 premiers ingrédients
        
        url = f"{FORKIFY_BASE_URL}/recipes"
        params = {
            'search': query,
        }
        
        print(f"Requête API Forkify: {url}")
        print(f"Paramètres: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Statut HTTP: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erreur API: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        # Forkify retourne: {'status': 'success', 'results': X, 'data': {'recipes': [...]}}
        if isinstance(data, dict) and data.get('status') == 'success':
            recipes = data.get('data', {}).get('recipes', [])
            if not recipes:
                # Essayer une autre structure possible
                recipes = data.get('recipes', [])
            print(f"Recettes trouvées: {len(recipes)}")
            if recipes:
                return recipes[:nombre_recettes]
        
        print(f"Format de réponse inattendu: {data}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur API Forkify: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse d'erreur: {e.response.text}")
        return []
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        return []

def obtenir_details_recette(recette_id):
    """
    Obtient les détails complets d'une recette
    
    Args:
        recette_id: ID de la recette dans Forkify
    
    Returns:
        Dictionnaire contenant les détails de la recette
    """
    try:
        url = f"{FORKIFY_BASE_URL}/recipes/{recette_id}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Erreur API Forkify (détails): {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # Forkify retourne: {'status': 'success', 'data': {'recipe': {...}}}
        if isinstance(data, dict) and data.get('status') == 'success':
            return data.get('data', {}).get('recipe', {})
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur API Forkify (détails): {e}")
        return None

def obtenir_instructions_recette(recette_data):
    """
    Obtient les instructions de préparation d'une recette
    Note: Forkify ne fournit pas d'instructions directement, mais un source_url
    
    Args:
        recette_data: Dictionnaire contenant les données de la recette
    
    Returns:
        Liste des étapes de préparation (vide car Forkify ne fournit pas d'instructions)
    """
    # Forkify ne fournit pas d'instructions dans l'API
    # Il fournit un source_url vers la recette originale
    return []

