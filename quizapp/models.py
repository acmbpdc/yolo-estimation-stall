from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #points = models.IntegerField(default=0)  # Points earned by the user
    total_score = models.FloatField(default=0)  # New field to track total score
    has_completed_quiz = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    score = models.FloatField(default=0)  # Score for the specific attempt
    answer = models.CharField(max_length=255)  # User's answer (predicted)
    actual = models.IntegerField(default=0)  # Correct answer (actual)
    predicted = models.IntegerField(default=0)  # User's prediction

    def calculate_score(self):
        """Calculate the score using the formula 100 - |actual - predicted|"""
        return 100 - abs(self.actual - self.predicted)

    def __str__(self):
        return f"{self.user.username} - {self.question}"

class Question(models.Model):
    text = models.CharField(max_length=255)  # The question text
    correct_answer = models.CharField(max_length=255)  # The correct answer
    statistic_question = models.CharField(default='a', max_length=255, null=True)
    statistic_correct_answer = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.text


