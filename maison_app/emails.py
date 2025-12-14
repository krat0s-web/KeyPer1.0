"""
Module pour gérer l'envoi d'emails dans l'application KeyPer
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def envoyer_invitation_email(invitation, email_destinataire, lien_invitation, foyer_nom, admin_nom=None):
    """
    Envoie un email d'invitation à un utilisateur
    
    Args:
        invitation: Instance du modèle Invitation
        email_destinataire: Email du destinataire
        lien_invitation: Lien complet pour rejoindre le foyer
        foyer_nom: Nom du foyer
        admin_nom: Nom de l'administrateur qui envoie l'invitation (optionnel)
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    try:
        # Préparer le contexte pour le template
        context = {
            'invitation': invitation,
            'lien_invitation': lien_invitation,
            'code_invitation': str(invitation.code),
            'foyer_nom': foyer_nom,
            'admin_nom': admin_nom or 'Administrateur',
            'role_display': invitation.get_role_display(),
            'nom_invitation': invitation.nom or 'Invitation',
        }
        
        # Rendre le template HTML
        html_message = render_to_string('maison_app/emails/invitation_email.html', context)
        
        # Rendre le template texte brut (fallback)
        plain_message = render_to_string('maison_app/emails/invitation_email.txt', context)
        
        # Sujet de l'email
        subject = f"🎉 Invitation à rejoindre le foyer {foyer_nom} - KeyPer"
        
        # Envoyer l'email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'KeyPer <noreply@keyper.com>',
            recipient_list=[email_destinataire],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email d'invitation: {str(e)}")
        return False

