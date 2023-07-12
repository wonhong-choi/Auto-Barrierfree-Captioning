from django.db import models
from django.contrib.auth.models import AbstractUser
import os
# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=10)
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    file = models.FileField(upload_to='post_files/')
    language = models.CharField(max_length=10)
    
    def __str__(self):
        return self.title
    
    def get_filename(self):
        return os.path.basename(self.file.name)
    
class Video(models.Model):
    file = models.FileField(upload_to='temp_video/')
    
    def get_filename(self):
        return os.path.basename(self.file.name)
    
    def get_file_path(self):
        return os.path.abspath(self.file.path)
    
