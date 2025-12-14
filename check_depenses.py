import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_taches_project.settings')
django.setup()

from maison_app.models import Depense, Foyer
from django.utils import timezone

# Récupérer tous les foyers
foyers = Foyer.objects.all()
print(f"\n🏠 Nombre de foyers: {foyers.count()}")

for foyer in foyers:
    print(f"\n📊 Foyer: {foyer.nom}")
    depenses = Depense.objects.filter(id_foyer=foyer)
    print(f"   Total dépenses: {depenses.count()}")
    
    if depenses.exists():
        print("\n   Détail des dépenses:")
        for dep in depenses:
            print(f"   - {dep.description}: {dep.montant}€")
            print(f"     Catégorie: {dep.categorie.nom if dep.categorie else 'Aucune'}")
            print(f"     Date: {dep.date_depense}")
            print(f"     Créée par: {dep.id_user.nom if dep.id_user else 'Inconnu'}")
    
    # Vérifier les dépenses des 30 derniers jours
    from datetime import timedelta
    today = timezone.now().date()
    date_30_jours = today - timedelta(days=30)
    depenses_30j = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=date_30_jours
    )
    print(f"\n   📅 Dépenses des 30 derniers jours: {depenses_30j.count()}")
    
    # Calcul par période
    lundi = today - timedelta(days=today.weekday())
    depenses_semaine = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=lundi
    )
    print(f"   Cette semaine: {depenses_semaine.count()} dépenses")
    
    mois_debut = today.replace(day=1)
    depenses_mois = Depense.objects.filter(
        id_foyer=foyer,
        date_depense__gte=mois_debut
    )
    print(f"   Ce mois: {depenses_mois.count()} dépenses")

print("\n✅ Vérification terminée!")
