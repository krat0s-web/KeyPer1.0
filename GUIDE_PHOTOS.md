# 📸 Guide d'Upload de Photos - Gestion Tâches

## 📁 Répertoires pour les Photos

Les photos sont automatiquement organisées dans le dossier **`media/`** à la racine du projet :

```
gestion_taches_web/
├── media/                    ← Dossier principal des photos
│   ├── foyers/              ← Photos des foyers
│   ├── pieces/              ← Photos des pièces
│   ├── animaux/             ← Photos des animaux
│   └── .gitkeep            ← Pour initialiser le dossier
├── manage.py
├── db.sqlite3
└── ... autres fichiers
```

## 🏠 Comment Uploader des Photos

### 1. **Photos de Foyer**
   - Allez sur : **Créer un Foyer** (`/creer-foyer/`)
   - Remplissez le nom du foyer
   - Cliquez sur **"📷 Photo du foyer"** et sélectionnez une image
   - Format accepté : JPG, PNG
   - Taille max : 5 MB
   - Les photos seront sauvegardées dans : `media/foyers/`

### 2. **Photos de Pièce**
   - Allez sur : **Ajouter une Pièce** (`/ajouter-piece/`)
   - Entrez le nom de la pièce
   - Cliquez sur **"📷 Photo de la pièce"** et sélectionnez une image
   - Format accepté : JPG, PNG
   - Taille max : 5 MB
   - Les photos seront sauvegardées dans : `media/pieces/`

### 3. **Photos d'Animal**
   - Allez sur : **Ajouter un Animal** (`/ajouter-animal/`)
   - Entrez le nom de l'animal
   - Sélectionnez la pièce (optionnel)
   - Cliquez sur **"📷 Photo de l'animal"** et sélectionnez une image
   - Format accepté : JPG, PNG
   - Taille max : 5 MB
   - Les photos seront sauvegardées dans : `media/animaux/`

## 🎨 Affichage des Photos

Les photos apparaîtront automatiquement :
- **Liste des foyers** : Cards avec miniatures
- **Détail du foyer** : Galerie des pièces et animaux avec photos
- **Dashboard** : Peut être étendu pour afficher les photos

## 📌 Où Mettre Vos Photos Localement

Si vous voulez **placer des photos manuellement** dans le projet avant les uploads :

1. Créez les dossiers (s'ils n'existent pas) :
   ```
   media/foyers/
   media/pieces/
   media/animaux/
   ```

2. Placez vos images JPG ou PNG directement dans ces dossiers

3. Les images seront automatiquement accessibles dans l'application

## ⚙️ Configuration Technique

La configuration Django a été mise à jour dans `settings.py` :
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Les routes pour servir les médias sont configurées dans `urls.py`.

## 🚀 Points Importants

- ✅ Les uploads sont **optionnels** pour tous les éléments
- ✅ Les photos sont affichées avec un **object-fit: cover** pour respecter les dimensions
- ✅ Les photos par défaut affichent des **icônes Bootstrap** si aucune image n'est fournie
- ✅ Les photos sont stockées dans des **dossiers organisés** par type
- ✅ Les images sont **compressées** par le navigateur automatiquement

## 📸 Conseils pour les Photos

- **Résolution** : 800x600px ou plus (idéal)
- **Format** : JPG pour les photos, PNG pour les icônes
- **Taille** : < 1 MB pour une meilleure performance
- **Noms de fichiers** : Sans accents, sans espaces (exemple: `cuisine-1.jpg`)

## 🔧 Troubleshooting

**Q : Mes photos ne s'affichent pas ?**
- Assurez-vous que le fichier est en JPG ou PNG
- Vérifiez que le fichier n'est pas corrompu
- Réessayez avec une autre photo

**Q : Erreur "fichier trop volumineux" ?**
- Le fichier dépasse 5 MB
- Compressez l'image avec un outil en ligne
- Essayez avec une résolution inférieure

**Q : Où accéder aux fichiers uploadés ?**
- Localisation : `gestion_taches_web/media/`
- URL en développement : `http://localhost:8000/media/foyers/...`

---
💡 **Astuce** : Pour un meilleur rendu, prenez des photos bien éclairées et nettes !
