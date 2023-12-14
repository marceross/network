from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, blank=True, related_name="followers")
    following_users = models.ManyToManyField(User, blank=True, related_name="following_users")

    def __str__(self):
        return f"{self.user.username} Followers: {self.followers.count()} Following: {self.following_users.count()}"

class Post(models.Model):
    post = models.CharField(max_length=280, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} by {self.created_by} at {self.created_date}"