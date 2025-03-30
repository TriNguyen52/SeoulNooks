from django.apps import AppConfig


class ColiversConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'colivers'

    def ready(self):
        import colivers.signals  # Import the signals
