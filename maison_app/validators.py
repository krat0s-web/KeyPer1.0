"""
Validateurs personnalisés pour les formulaires
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta


def validate_date_limite(value):
    """Valide que la date limite n'est pas dans le passé"""
    if value and value < date.today():
        raise ValidationError(
            _('La date limite ne peut pas être dans le passé.'),
            code='date_passee'
        )


def validate_date_limite_future(value):
    """Valide que la date limite n'est pas trop loin dans le futur (max 2 ans)"""
    if value:
        max_date = date.today() + timedelta(days=730)  # 2 ans
        if value > max_date:
            raise ValidationError(
                _('La date limite ne peut pas être plus de 2 ans dans le futur.'),
                code='date_trop_loin'
            )


def validate_temps_estime(value):
    """Valide que le temps estimé est raisonnable (max 24h = 1440 minutes)"""
    if value and value > 1440:
        raise ValidationError(
            _('Le temps estimé ne peut pas dépasser 24 heures (1440 minutes).'),
            code='temps_trop_long'
        )
    if value and value < 0:
        raise ValidationError(
            _('Le temps estimé doit être positif.'),
            code='temps_negatif'
        )


def validate_titre_tache(value):
    """Valide le titre d'une tâche"""
    if not value or len(value.strip()) < 3:
        raise ValidationError(
            _('Le titre doit contenir au moins 3 caractères.'),
            code='titre_trop_court'
        )
    if len(value) > 100:
        raise ValidationError(
            _('Le titre ne peut pas dépasser 100 caractères.'),
            code='titre_trop_long'
        )


def validate_montant_budget(value):
    """Valide le montant d'un budget"""
    if value and value < 0:
        raise ValidationError(
            _('Le montant doit être positif.'),
            code='montant_negatif'
        )
    if value and value > 1000000:
        raise ValidationError(
            _('Le montant ne peut pas dépasser 1 000 000€.'),
            code='montant_trop_eleve'
        )


def validate_date_rappel(value):
    """Valide que la date de rappel est cohérente avec la date limite"""
    # Cette validation sera utilisée dans le modèle ou la vue
    pass

