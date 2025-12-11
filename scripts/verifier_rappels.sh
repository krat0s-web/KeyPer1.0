#!/bin/bash
# Script shell pour exécuter la commande verifier_rappels sur Linux/Mac
# Ce script doit être exécuté par un cron job

# Obtenir le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Aller dans le répertoire du projet
cd "$PROJECT_DIR" || exit 1

# Activer l'environnement virtuel si présent
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Exécuter la commande Django
python manage.py verifier_rappels

# Désactiver l'environnement virtuel
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

