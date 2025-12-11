#!/bin/bash
# Script shell pour configurer le cron job sur Linux/Mac
# Exécutez ce script pour ajouter automatiquement le cron job

# Obtenir le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPT_PATH="$SCRIPT_DIR/verifier_rappels.sh"

# Vérifier que le script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Le script verifier_rappels.sh est introuvable."
    echo "Chemin attendu: $SCRIPT_PATH"
    exit 1
fi

# Rendre le script exécutable
chmod +x "$SCRIPT_PATH"

# Créer la ligne cron (tous les jours à 8h00)
CRON_LINE="0 8 * * * $SCRIPT_PATH >> $PROJECT_DIR/logs/cron_rappels.log 2>&1"

# Créer le répertoire logs s'il n'existe pas
mkdir -p "$PROJECT_DIR/logs"

# Vérifier si la ligne existe déjà dans crontab
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
    echo "⚠️  Le cron job existe déjà dans crontab."
    read -p "Voulez-vous le remplacer ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        # Supprimer l'ancienne ligne
        crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH" | crontab -
        # Ajouter la nouvelle ligne
        (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
        echo "✅ Cron job mis à jour avec succès !"
    else
        echo "❌ Opération annulée."
        exit 0
    fi
else
    # Ajouter la nouvelle ligne
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ Cron job ajouté avec succès !"
fi

echo ""
echo "Détails de la configuration:"
echo "   Horaire: Tous les jours à 8h00"
echo "   Script: $SCRIPT_PATH"
echo "   Logs: $PROJECT_DIR/logs/cron_rappels.log"
echo ""
echo "Pour vérifier le cron job: crontab -l"
echo "Pour éditer le cron job: crontab -e"
echo "Pour supprimer le cron job: crontab -l | grep -v '$SCRIPT_PATH' | crontab -"

