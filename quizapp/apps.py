from django.apps import AppConfig


class quizappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizapp'
    
    def ready(self):
        import quizapp.signals  # Replace with your actual app name
