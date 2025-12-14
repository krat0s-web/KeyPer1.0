"""
Module pour traduire les recettes en français
"""
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("deep-translator non installé. Installation: pip install deep-translator")

def traduire_en_francais(texte, source_lang='en'):
    """
    Traduit un texte en français
    
    Args:
        texte: Texte à traduire
        source_lang: Langue source (par défaut 'en' pour anglais)
    
    Returns:
        Texte traduit en français, ou texte original si erreur
    """
    if not texte or not TRANSLATOR_AVAILABLE:
        return texte
    
    # Convertir en string si nécessaire
    if not isinstance(texte, str):
        texte = str(texte)
    
    # Si le texte est vide, retourner tel quel
    if not texte.strip():
        return texte
    
    # Si le texte est déjà en français (détection simple), ne pas traduire
    if any(char in texte for char in 'àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ'):
        return texte
    
    try:
        translator = GoogleTranslator(source='auto', target='fr')
        # Limiter la longueur pour éviter les erreurs (Google Translate a une limite)
        if len(texte) > 5000:
            # Traduire par morceaux
            chunks = [texte[i:i+5000] for i in range(0, len(texte), 5000)]
            traductions = []
            for chunk in chunks:
                try:
                    trad = translator.translate(chunk)
                    traductions.append(trad if trad else chunk)
                except:
                    traductions.append(chunk)
            texte_traduit = ' '.join(traductions)
        else:
            texte_traduit = translator.translate(texte)
        
        # Vérifier que la traduction a bien eu lieu
        if texte_traduit and texte_traduit != texte:
            print(f"Traduction réussie: '{texte[:50]}...' -> '{texte_traduit[:50]}...'")
            return texte_traduit
        else:
            print(f"Traduction non effectuée pour: '{texte[:50]}...'")
            return texte
    except Exception as e:
        print(f"Erreur de traduction pour '{texte[:50]}...': {e}")
        return texte

def traduire_recette(recette_data):
    """
    Traduit tous les champs d'une recette en français
    
    Args:
        recette_data: Dictionnaire contenant les données de la recette
    
    Returns:
        Dictionnaire avec les champs traduits
    """
    recette_traduite = recette_data.copy()
    
    # Traduire le titre (peut être dans 'titre' ou 'title')
    titre = recette_traduite.get('titre') or recette_traduite.get('title', '')
    if titre:
        recette_traduite['titre'] = traduire_en_francais(titre)
        if 'title' in recette_traduite:
            recette_traduite['title'] = recette_traduite['titre']
    
    # Traduire les ingrédients
    ingredients = recette_traduite.get('ingredients', '')
    if ingredients:
        recette_traduite['ingredients'] = traduire_en_francais(ingredients)
    
    # Traduire les instructions
    instructions = recette_traduite.get('instructions', '')
    if instructions:
        recette_traduite['instructions'] = traduire_en_francais(instructions)
    
    # Traduire le résumé si présent
    summary = recette_traduite.get('summary', '')
    if summary:
        recette_traduite['summary'] = traduire_en_francais(summary)
    
    return recette_traduite

