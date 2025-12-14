from django.apps import AppConfig


class MaisonAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maison_app'
    
    def ready(self):
        """Importe les signaux quand l'application est prête"""
        import maison_app.signals