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
    pub_date = models.DateTimeField('Date published', null=True, blank=True)
    
    def is_published(self):
        return self.pub_date is not None and self.pub_date <= datetime.datetime.now()
    is_published.boolean = True
    
    def __unicode__(self):
        return u"%s | %s | %s" % (self.title, self.pub_date, self.is_published())
