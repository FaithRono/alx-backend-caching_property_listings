from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        """
        Import signals when Django starts.
        This ensures that signal handlers are connected.
        """
        import properties.signals
