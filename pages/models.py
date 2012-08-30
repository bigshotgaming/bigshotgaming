from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User 

class Post(models.Model):

    CATEGORY_CHOICES = (
        ('N', 'News'),
        ('R', 'Reviews'),
    )

    def __unicode__(self):
        return self.title

    title = models.CharField(max_length=80)
    body = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey("auth.User", limit_choices_to={'is_staff': True})
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='N')
 