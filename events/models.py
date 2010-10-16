from django.db import models
from django.contrib.localflavor.us.models import USStateField

class Event(models.Model):

    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=100, verbose_name='Event Name')
    description = models.TextField(verbose_name='Event Description')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.ForeignKey('Venue')
    participant_limit = models.IntegerField()
    contact_email = models.EmailField()
    other_details = models.TextField()

    
class Venue(models.Model):
    
    def __unicode__(self):
        return self.name
        
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=30)
    state = USStateField()
    zipcode = models.CharField(max_length=10)
        
        