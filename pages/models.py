from django.db import models
import datetime

# Create your models here.
class Section(models.Model):
    
    class Meta:
        ordering = ('ordering', 'id')
    
    name = models.CharField(blank=False, null=False, max_length=150)
    url = models.SlugField()
    posts = models.ManyToManyField('Post')
    ordering = models.PositiveIntegerField()
    posts_to_show = models.SmallIntegerField(default=5, blank=False, null=False)
    
    def __unicode__(self):
        return self.name
    
class Post(models.Model):
    title = models.CharField(blank=False, null=False, max_length=150)
    content = models.TextField('Message content', help_text='Use Markdown syntax.')
    pub_date = models.DateTimeField('Date published', default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.title
