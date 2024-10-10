from django.contrib.auth.models import User
from django.db import models

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    score = models.IntegerField(default=0)
    answer = models.CharField(max_length=255)
