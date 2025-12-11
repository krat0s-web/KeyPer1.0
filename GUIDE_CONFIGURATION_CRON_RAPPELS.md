# 🔔 Guide de Configuration des Rappels Automatiques

Ce guide explique comment configurer l'exécution automatique quotidienne de la commande `verifier_rappels` pour envoyer les notifications de rappel des tâches.

## 📋 Prérequis

- La commande Django `verifier_rappels` est déjà implémentée
- Le projet Django est fonctionnel
- Python est installé et accessible depuis la ligne de commande

## 🪟 Configuration sur Windows

### Méthode 1 : Script PowerShell automatique (Recommandé)

1. **Ouvrez PowerShell en tant qu'administrateur**
   - Clic droit sur PowerShell → "Exécuter en tant qu'administrateur"

2. **Naviguez vers le répertoire du projet**
   ```powershell
   cd C:\0-Projet_KEYPER_sans_maj_Jorys\KeyPer
   ```

3. **Exécutez le script d'installation**
   ```powershell
   .\scripts\install_cron_windows.ps1
   ```

4. **Vérifiez la configuration**
   - Ouvrez le **Planificateur de tâches Windows**
   - Cherchez la tâche nommée `KeyPer-VerifierRappels`
   - Elle devrait s'exécuter tous les jours à 8h00

### Méthode 2 : Configuration manuelle

1. **Ouvrez le Planificateur de tâches Windows**
   - Appuyez sur `Win + R`, tapez `taskschd.msc` et appuyez sur Entrée

2. **Créez une tâche de base**
   - Cliquez sur "Créer une tâche de base" dans le panneau de droite

3. **Configurez la tâche**
   - **Nom** : `KeyPer-VerifierRappels`
   - **Description** : `Vérifie les rappels automatiques des tâches KeyPer`
   - **Déclencheur** : Quotidien, à 8h00
   - **Action** : Démarrer un programme
     - **Programme** : `C:\0-Projet_KEYPER_sans_maj_Jorys\KeyPer\scripts\verifier_rappels.bat`
     - **Dossier de départ** : `C:\0-Projet_KEYPER_sans_maj_Jorys\KeyPer`

4. **Paramètres avancés**
   - Cochez "Exécuter que l'utilisateur soit connecté ou non"
   - Cochez "Ne pas stocker le mot de passe"
   - Cochez "Exécuter avec les privilèges les plus élevés"

### Test manuel

Pour tester la commande manuellement :

```powershell
cd C:\0-Projet_KEYPER_sans_maj_Jorys\KeyPer
python manage.py verifier_rappels
```

## 🐧 Configuration sur Linux/Mac

### Méthode 1 : Script shell automatique (Recommandé)

1. **Ouvrez un terminal**

2. **Naviguez vers le répertoire du projet**
   ```bash
   cd /chemin/vers/KeyPer
   ```

3. **Rendez le script exécutable**
   ```bash
   chmod +x scripts/install_cron_linux.sh
   ```

4. **Exécutez le script d'installation**
   ```bash
   ./scripts/install_cron_linux.sh
   ```

5. **Vérifiez la configuration**
   ```bash
   crontab -l
   ```
   Vous devriez voir une ligne comme :
   ```
   0 8 * * * /chemin/vers/KeyPer/scripts/verifier_rappels.sh >> /chemin/vers/KeyPer/logs/cron_rappels.log 2>&1
   ```

### Méthode 2 : Configuration manuelle

1. **Ouvrez l'éditeur crontab**
   ```bash
   crontab -e
   ```

2. **Ajoutez la ligne suivante** (ajustez le chemin selon votre installation)
   ```bash
   0 8 * * * cd /chemin/vers/KeyPer && /chemin/vers/python manage.py verifier_rappels >> /chemin/vers/KeyPer/logs/cron_rappels.log 2>&1
   ```

   Ou si vous utilisez un environnement virtuel :
   ```bash
   0 8 * * * cd /chemin/vers/KeyPer && source venv/bin/activate && python manage.py verifier_rappels >> /chemin/vers/KeyPer/logs/cron_rappels.log 2>&1
   ```

3. **Sauvegardez et quittez** (dans vim : `:wq`, dans nano : `Ctrl+X` puis `Y`)

### Test manuel

Pour tester la commande manuellement :

```bash
cd /chemin/vers/KeyPer
python manage.py verifier_rappels
```

Ou avec l'environnement virtuel :

```bash
cd /chemin/vers/KeyPer
source venv/bin/activate
python manage.py verifier_rappels
```

## 📝 Format du Cron Job

Le format de la ligne cron est : `minute heure jour mois jour-semaine commande`

- `0 8 * * *` signifie : tous les jours à 8h00
- Pour changer l'heure, modifiez le `8` (format 24h)
- Pour exécuter plusieurs fois par jour, ajoutez plusieurs lignes

Exemples :
- `0 8 * * *` : Tous les jours à 8h00
- `0 8,20 * * *` : Tous les jours à 8h00 et 20h00
- `0 */6 * * *` : Toutes les 6 heures
- `0 8 * * 1-5` : Du lundi au vendredi à 8h00

## 🔍 Vérification et Dépannage

### Vérifier que le cron job fonctionne

**Windows :**
1. Ouvrez le Planificateur de tâches
2. Trouvez la tâche `KeyPer-VerifierRappels`
3. Cliquez dessus et vérifiez l'historique d'exécution

**Linux/Mac :**
1. Vérifiez les logs :
   ```bash
   tail -f /chemin/vers/KeyPer/logs/cron_rappels.log
   ```

2. Vérifiez les logs système :
   ```bash
   # Sur Linux
   grep CRON /var/log/syslog
   
   # Sur Mac
   grep cron /var/log/system.log
   ```

### Problèmes courants

1. **Le script ne s'exécute pas**
   - Vérifiez que Python est dans le PATH
   - Vérifiez que le chemin du projet est correct
   - Vérifiez les permissions d'exécution (Linux/Mac)

2. **Erreur "Module not found"**
   - Assurez-vous que l'environnement virtuel est activé
   - Vérifiez que toutes les dépendances sont installées

3. **Erreur "Permission denied"**
   - Sur Linux/Mac, vérifiez les permissions du script : `chmod +x scripts/verifier_rappels.sh`
   - Sur Windows, exécutez le script d'installation en tant qu'administrateur

4. **Les notifications ne sont pas créées**
   - Vérifiez que des tâches ont une `date_rappel` définie
   - Vérifiez que les tâches ne sont pas déjà terminées
   - Exécutez la commande manuellement pour voir les messages d'erreur

## 🗑️ Désinstallation

### Windows

1. Ouvrez le Planificateur de tâches
2. Trouvez la tâche `KeyPer-VerifierRappels`
3. Clic droit → Supprimer

Ou via PowerShell :
```powershell
Unregister-ScheduledTask -TaskName "KeyPer-VerifierRappels" -Confirm:$false
```

### Linux/Mac

```bash
crontab -l | grep -v "verifier_rappels" | crontab -
```

## 📚 Ressources supplémentaires

- [Documentation Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Documentation Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Documentation Cron](https://en.wikipedia.org/wiki/Cron)

