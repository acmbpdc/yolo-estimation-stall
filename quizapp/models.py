from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)  # Default points set to 0
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question',on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # Score for the specific attempt
    answer = models.CharField(max_length=255)  # User's answer

    def __str__(self):
        return f"{self.user.username} - {self.question}"

class Question(models.Model):
    text = models.CharField(max_length=255)  # The question text
    correct_answer = models.CharField(max_length=255)  # The correct answer
    # You can add other fields like choices if you want multiple-choice questions

    def __str__(self):
        return self.text
