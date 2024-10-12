from django.contrib import admin
from .models import UserProfile, QuizAttempt,Question

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(QuizAttempt)
admin.site.register(Question)