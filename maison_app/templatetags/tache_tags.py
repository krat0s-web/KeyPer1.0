from django import template

register = template.Library()

@register.filter
def has_demande_en_attente(tache, user):
    """Template filter pour vérifier si une tâche a une demande en attente pour un utilisateur"""
    if not tache or not user:
        return False
    return tache.has_demande_en_attente_for_user(user)

