"""
Signals Django pour gérer automatiquement les relations entre utilisateurs et foyers
"""
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Utilisateur


@receiver(m2m_changed, sender=Utilisateur.foyers.through)
def gerer_foyer_actif(sender, instance, action, pk_set, **kwargs):
    """
    Signal qui se déclenche quand un utilisateur est ajouté ou retiré d'un foyer.
    Définit automatiquement le foyer actif si l'utilisateur n'en a pas.
    """
    # Seulement pour les actions 'post_add' (après ajout) et 'post_remove' (après retrait)
    if action in ['post_add', 'post_remove']:
        # Recharger l'utilisateur depuis la base de données pour avoir les foyers à jour
        try:
            utilisateur = Utilisateur.objects.select_related('foyer_actif').prefetch_related('foyers').get(pk=instance.pk)
        except Utilisateur.DoesNotExist:
            return
        
        # Si l'utilisateur a des foyers
        if utilisateur.foyers.exists():
            # Si l'utilisateur n'a pas de foyer actif, définir le premier comme actif
            if not utilisateur.foyer_actif:
                utilisateur.foyer_actif = utilisateur.foyers.first()
                utilisateur.save(update_fields=['foyer_actif'])
            # Si le foyer actif n'est plus dans la liste des foyers, définir le premier disponible
            elif utilisateur.foyer_actif not in utilisateur.foyers.all():
                utilisateur.foyer_actif = utilisateur.foyers.first()
                utilisateur.save(update_fields=['foyer_actif'])
        else:
            # Si l'utilisateur n'a plus de foyers, retirer le foyer actif
            if utilisateur.foyer_actif:
                utilisateur.foyer_actif = None
                utilisateur.save(update_fields=['foyer_actif'])

