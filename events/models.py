from django.db import models
from django.contrib.localflavor.us.models import USStateField
from django.contrib.auth.models import User
from django.forms import ModelForm
import uuid

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
        return '%s - %s' % (self.user.username, self.event)
    
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

class Coupon(models.Model):
    
    def __unicode__(self):
        return self.uuid
           
    def make_uuid():
        return str(uuid.uuid4())
        
    uuid = models.CharField(max_length=36, primary_key=True, default=make_uuid, editable=False)
    

class Ticket(models.Model):
    
    def __unicode__(self):
        return '%s - %s' % (self.participant.user.username, self.participant.event)

    participant = models.ForeignKey(Participant)
    #event = models.ForeignKey(Event)
    coupon = models.OneToOneField(Coupon, null=True)

    
    
    
    
