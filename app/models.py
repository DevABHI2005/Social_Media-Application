from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank = True)
    profileimg = models.ImageField(upload_to = 'profile_images', default = 'blank-profile-picture.png')
    location = models.CharField(max_length = 100, blank = True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images', blank=True)
    caption = models.TextField()
    created_at = models.DateTimeField(default= datetime.now)
    likes = models.IntegerField(default = 0)

class LikePost(models.Model):
    post_id = models.CharField(max_length = 500)
    username = models.CharField(max_length = 100)

    def __str__(self):
        return self.username

# class Comment(models.Model):
#     post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    

    # def __str__(self):
    #     return self.user
    

class FollowersCount(models.Model):
    follower = models.CharField(max_length = 100)
    user = models.CharField(max_length = 100)

    def __str__(self):
        return self.user

