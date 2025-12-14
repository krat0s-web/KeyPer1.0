"""
Module pour interagir avec l'API Spoonacular Recipe
Documentation: https://spoonacular.com/food-api/docs
"""
import requests

SPOONACULAR_API_KEY = '40cb1e6ea3a24b88b04f715623397052'
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'

def rechercher_recettes_par_ingredients(ingredients, nombre_recettes=10):
    """
    Recherche des recettes basées sur une liste d'ingrédients via l'API Spoonacular
    
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
        
        # Spoonacular utilise un paramètre 'ingredients' avec les ingrédients séparés par des virgules
        ingredients_str = ','.join(ingredients_clean)
        
        url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
        params = {
            'ingredients': ingredients_str,
            'number': min(nombre_recettes, 20),  # Limite de l'API
            'ranking': 2,  # 1 = maximize used ingredients, 2 = minimize missing ingredients
            'ignorePantry': 'true',
            'apiKey': SPOONACULAR_API_KEY
        }
        
        print(f"Requête API Spoonacular: {url}")
        print(f"Paramètres: {params}")
        
        response = requests.get(url, params=params, timeout=15)
        
        print(f"Statut HTTP: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erreur API: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        # Spoonacular retourne une liste de recettes avec des IDs
        if isinstance(data, list) and len(data) > 0:
            print(f"Recettes trouvées: {len(data)}")
            
            # Récupérer les détails complets de chaque recette
            recettes_detaillees = []
            recette_ids = [recette['id'] for recette in data[:nombre_recettes]]
            
            if recette_ids:
                # Récupérer les informations détaillées en batch
                ids_str = ','.join(map(str, recette_ids))
                url_details = f"{SPOONACULAR_BASE_URL}/informationBulk"
                params_details = {
                    'ids': ids_str,
                    'apiKey': SPOONACULAR_API_KEY
                }
                
                response_details = requests.get(url_details, params=params_details, timeout=15)
                
                if response_details.status_code == 200:
                    recettes_detaillees = response_details.json()
                else:
                    print(f"Erreur lors de la récupération des détails: {response_details.status_code}")
                    # Utiliser les données de base si les détails échouent
                    recettes_detaillees = data[:nombre_recettes]
            
            # Formater les recettes pour correspondre au format attendu
            recettes_formatees = []
            for recette in recettes_detaillees[:nombre_recettes]:
                recette_formatee = {
                    'id': recette.get('id', ''),
                    'title': recette.get('title', 'Recette sans nom'),
                    'image': recette.get('image', ''),
                    'image_url': recette.get('image', ''),
                    'servings': recette.get('servings', ''),
                    'readyInMinutes': recette.get('readyInMinutes', ''),
                    'sourceUrl': recette.get('sourceUrl', ''),
                    'extendedIngredients': recette.get('extendedIngredients', []),
                    'instructions': recette.get('instructions', ''),
                    'summary': recette.get('summary', '')
                }
                
                # Formater les ingrédients
                if recette_formatee['extendedIngredients']:
                    ingredients_list = []
                    for ing in recette_formatee['extendedIngredients']:
                        ing_name = ing.get('name', '')
                        ing_amount = ing.get('amount', 0)
                        ing_unit = ing.get('unit', '')
                        if ing_amount and ing_unit:
                            ingredients_list.append(f"{ing_name} ({ing_amount} {ing_unit})")
                        else:
                            ingredients_list.append(ing_name)
                    recette_formatee['ingredients'] = ', '.join(ingredients_list)
                else:
                    recette_formatee['ingredients'] = ''
                
                # Nettoyer les instructions HTML si présentes
                instructions = recette_formatee.get('instructions', '')
                if instructions:
                    # Supprimer les balises HTML simples
                    import re
                    instructions = re.sub(r'<[^>]+>', '', instructions)
                    instructions = instructions.replace('&nbsp;', ' ').strip()
                    recette_formatee['instructions'] = instructions
                
                recettes_formatees.append(recette_formatee)
            
            return recettes_formatees
        
        print(f"Aucune recette trouvée")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur API Spoonacular: {e}")
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
        recette_id: ID de la recette dans Spoonacular
    
    Returns:
        Dictionnaire contenant les détails de la recette
    """
    try:
        url = f"{SPOONACULAR_BASE_URL}/{recette_id}/information"
        params = {
            'apiKey': SPOONACULAR_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des détails: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des détails: {e}")
        return None
