
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizapp'

    def ready(self):
        # Import signals here to avoid circular import issues
        import quizapp.signals        