from django.db import models
from datetime import date

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    genres = models.CharField(max_length=100)
    playtime = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='images', blank=True, null=True)
    likes = models.PositiveIntegerField()
    created_at =  models.DateField(default=date.today)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    
    def __str__(self):
        return self.title
