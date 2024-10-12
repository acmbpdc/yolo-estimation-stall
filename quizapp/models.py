from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)  # Default points set to 0
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    score = models.IntegerField(default=0)  # Score for the specific attempt
    answer = models.CharField(max_length=255)  # User's answer

    def __str__(self):
        return f"{self.user.username} - Question {self.question_number} Attempt"