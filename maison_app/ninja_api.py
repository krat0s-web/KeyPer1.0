"""
Module pour interagir avec l'API Ninja Recipe
Documentation: https://api-ninjas.com/api/recipe
"""
import requests

NINJA_API_KEY = 'fl8Oy8TsjmbTO+7RZKp8CA==PFQFhRFEFy0W6D0G'
NINJA_BASE_URL = 'https://api.api-ninjas.com/v1/recipe'

def rechercher_recettes_par_ingredients(ingredients, nombre_recettes=10):
    """
    Recherche des recettes basées sur une liste d'ingrédients via l'API Ninja
    
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
        
        # API Ninja utilise un paramètre 'query' avec les ingrédients séparés par des virgules ou espaces
        # On utilise le premier ingrédient principal comme recherche
        query = ingredients_clean[0] if ingredients_clean else ''
        
        url = NINJA_BASE_URL
        headers = {
            'X-Api-Key': NINJA_API_KEY
        }
        params = {
            'query': query,
        }
        
        print(f"Requête API Ninja: {url}")
        print(f"Paramètres: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Statut HTTP: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erreur API: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        # API Ninja retourne directement une liste de recettes
        if isinstance(data, list) and len(data) > 0:
            print(f"Recettes trouvées: {len(data)}")
            # Filtrer les recettes qui contiennent au moins un des ingrédients recherchés
            recettes_filtrees = []
            for recette in data[:nombre_recettes * 3]:  # Prendre plus pour filtrer
                ingredients_recette = recette.get('ingredients', '').lower()
                # Vérifier si au moins un ingrédient recherché est présent dans les ingrédients
                if ingredients_recette and any(ing in ingredients_recette for ing in ingredients_clean):
                    # S'assurer que l'image est présente dans la réponse
                    if 'image' not in recette and 'image_url' not in recette:
                        # Si pas d'image, on peut essayer de générer une URL d'image par défaut ou laisser vide
                        recette['image'] = ''
                    recettes_filtrees.append(recette)
                    if len(recettes_filtrees) >= nombre_recettes:
                        break
            
            # Si pas assez de recettes filtrées, prendre les premières disponibles
            if len(recettes_filtrees) < nombre_recettes:
                recettes_filtrees = data[:nombre_recettes]
            
            return recettes_filtrees[:nombre_recettes]
        
        print(f"Aucune recette trouvée")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur API Ninja: {e}")
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
    Note: L'API Ninja retourne déjà tous les détails dans la recherche
    
    Args:
        recette_id: ID de la recette (non utilisé pour Ninja, mais gardé pour compatibilité)
    
    Returns:
        Dictionnaire contenant les détails de la recette (None car non disponible)
    """
    # L'API Ninja retourne déjà tous les détails dans la recherche
    return None

def obtenir_instructions_recette(recette_data):
    """
    Obtient les instructions de préparation d'une recette
    
    Args:
        recette_data: Dictionnaire contenant les données de la recette
    
    Returns:
        Liste des étapes de préparation
    """
    instructions = recette_data.get('instructions', '')
    if instructions:
        # Séparer les instructions par les numéros ou points
        steps = [step.strip() for step in instructions.split('\n') if step.strip()]
        return steps
    return []

