from django.db import models
from django.contrib.auth.models import User

class RoadmapStep(models.Model):
    language = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    week = models.IntegerField()
    level = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.language} | {self.title}"
    

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roadmap_step = models.ForeignKey(RoadmapStep, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'roadmap_step')
        
        
        
# core/models.py
class CareerRoadmap(models.Model):
    role = models.CharField(max_length=100)                # e.g. "Python Developer"
    step_number = models.IntegerField()                   # 1,2,3...
    title = models.CharField(max_length=200)              # e.g. "Learn Core Python"
    description = models.TextField()                      # details
    
    
class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} streak"

