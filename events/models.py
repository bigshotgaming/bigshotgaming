from django.db import models
from django.contrib.localflavor.us.models import USStateField
from django.contrib.auth.models import User
from django.forms import ModelForm

class Event(models.Model):

    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=100, verbose_name='Event Name')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.ForeignKey('Venue')
    participant_limit = models.IntegerField()
    description = models.CharField(max_length=100)
    is_active = models.BooleanField()
    #participants = models.ManyToManyField('attendeereg.Attendee', blank=True)
    
class Venue(models.Model):
    
    def __unicode__(self):
        return self.name
        
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=30)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

class Participant(models.Model):
    
    def __unicode__(self):
        return self.user.username
    
    user = models.OneToOneField(User)

class Ticket(models.Model):
    
    def __unicode__(self):
        return '%s - %s' % (self.participant.user.username, self.event)

    
    is_paid = models.BooleanField()
    participant = models.ForeignKey(Participant)
    event = models.ForeignKey(Event)
    
    
