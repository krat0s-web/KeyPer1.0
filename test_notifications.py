#!/usr/bin/env python
"""
Script de test pour créer des notifications manuellement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_taches_project.settings')
django.setup()

from maison_app.models import Notification, Utilisateur, Foyer

# Récupère un utilisateur et un foyer pour tester
try:
    user = Utilisateur.objects.first()
    foyer = Foyer.objects.first()
    
    if not user or not foyer:
        print("❌ Aucun utilisateur ou foyer trouvé. Créez-en d'abord.")
        exit(1)
    
    # Créer différents types de notifications de test
    notification_types = [
        {
            'type': 'tache_assignee',
            'titre': '📋 Nouvelle tâche assignée',
            'message': 'Vous avez été assigné à la tâche "Faire les courses"'
        },
        {
            'type': 'tache_complete',
            'titre': '✅ Tâche complétée',
            'message': 'Alice a complété la tâche "Nettoyer la cuisine"'
        },
        {
            'type': 'budget_alerte',
            'titre': '💰 Alerte Budget',
            'message': 'Le budget pour "Courses" est à 85%'
        },
        {
            'type': 'nouveau_membre',
            'titre': '👥 Nouveau membre',
            'message': 'Bob a rejoint le foyer'
        }
    ]
    
    for notif_data in notification_types:
        notif = Notification.objects.create(
            id_user=user,
            type=notif_data['type'],
            titre=notif_data['titre'],
            message=notif_data['message'],
            id_foyer=foyer
        )
        print(f"✅ Notification créée: {notif_data['titre']}")
    
    print("\n✅ Toutes les notifications de test ont été créées !")
    print(f"👤 Utilisateur: {user.email}")
    print(f"🏠 Foyer: {foyer.nom}")
    
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
