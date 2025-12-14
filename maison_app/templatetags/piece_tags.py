from django import template

register = template.Library()

@register.filter
def peut_acceder(piece, user):
    """
    Vérifie si un utilisateur peut accéder à une pièce.
    """
    if not user or not user.is_authenticated:
        return False
    return piece.peut_acceder(user)

