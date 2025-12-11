# Problème avec la clé API Spoonacular

## Diagnostic

L'API Spoonacular retourne une erreur **401 (Non autorisé)** avec le message :
```
"You are not authorized. Please read https://spoonacular.com/food-api/docs#Authentication"
```

## Causes possibles

1. **Clé API invalide ou expirée** : La clé fournie (`de5b1e76b21048f98f035419303c947a`) n'est peut-être plus valide
2. **Limite de requêtes atteinte** : Les clés API gratuites ont des quotas quotidiens limités
3. **Clé API désactivée** : La clé peut avoir été désactivée pour violation des conditions d'utilisation

## Solutions

### Option 1 : Obtenir une nouvelle clé API

1. Allez sur https://spoonacular.com/food-api
2. Créez un compte gratuit
3. Obtenez une nouvelle clé API
4. Remplacez la clé dans `maison_app/spoonacular_api.py` :
   ```python
   SPOONACULAR_API_KEY = 'VOTRE_NOUVELLE_CLE_ICI'
   ```

### Option 2 : Vérifier votre clé actuelle

1. Connectez-vous à votre compte Spoonacular
2. Vérifiez que la clé est active
3. Vérifiez votre quota de requêtes restantes
4. Si la clé est valide, le problème peut venir d'un autre endroit

### Option 3 : Utiliser une alternative

Si vous ne pouvez pas obtenir une clé API valide, vous pouvez :
- Utiliser une autre API de recettes (Edamam, Recipe Puppy, etc.)
- Créer une base de données locale de recettes
- Utiliser des recettes statiques prédéfinies

## Test de la clé API

Pour tester votre clé API, exécutez :
```bash
python test_spoonacular.py
```

Si vous obtenez toujours une erreur 401, la clé n'est pas valide.

## Documentation Spoonacular

- Documentation : https://spoonacular.com/food-api/docs
- Authentification : https://spoonacular.com/food-api/docs#Authentication

