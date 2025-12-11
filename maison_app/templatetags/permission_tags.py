from django import template
from maison_app.permissions import has_permission

register = template.Library()

@register.filter
def can(user, permission):
    """Vérifie si un utilisateur a une permission donnée."""
    if not user or not user.is_authenticated:
        return False
    return has_permission(user, permission)

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par sa clé."""
    if dictionary is None:
        return None
    return dictionary.get(key)

