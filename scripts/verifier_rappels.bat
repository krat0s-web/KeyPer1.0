@echo off
REM Script batch pour exécuter la commande verifier_rappels sur Windows
REM Ce script doit être exécuté par le Task Scheduler de Windows

REM Définir le répertoire du projet
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

REM Activer l'environnement virtuel si présent
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Exécuter la commande Django
python manage.py verifier_rappels

REM Désactiver l'environnement virtuel
if exist "venv\Scripts\deactivate.bat" (
    call venv\Scripts\deactivate.bat
)

