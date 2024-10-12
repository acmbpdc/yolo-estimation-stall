from django.contrib import admin
from .models import UserProfile, QuizAttempt

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(QuizAttempt)
