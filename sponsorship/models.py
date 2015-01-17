from datetime import datetime
from django.db import models
from localflavor.us.models import PhoneNumberField
from django.contrib.auth.models import User

# class SponsorManager(models.Manager):
#     def get_query_set(self):
#         return super(SponsorManager, self).get_query_set().annotate(prizecount=models.Count('prize'))

class Sponsor(models.Model):
    
    def __unicode__(self):
        return self.name     
    
    name = models.CharField(max_length=100, verbose_name="Sponsor Name")
    contact_name = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = PhoneNumberField(blank=True)
    lan_rep = models.ForeignKey(User, limit_choices_to={'is_staff':True}, verbose_name="LAN Representative")
    notes = models.TextField(blank=True)
    event = models.ManyToManyField('events.Event', through='EventSponsor')
    contact_form_url = models.URLField(blank=True, verbose_name='Contact Form URL')
    banner_url = models.URLField(blank=True, verbose_name='Banner URL')
    banner = models.ImageField(blank=True, upload_to='sponsor/banners/')
    featured_sponsor = models.BooleanField(default=False)
    featured_banner = models.ImageField(blank=True, upload_to='sponsor/featured/')
    # objects = SponsorManager()
    
    # def count(self):
    #     return self.prizecount
    # count.admin_order_field = 'prizecount'

class EventSponsor(models.Model):
    
    STATUS_TYPES = (
        ('c', 'Confirmed'),
        ('d', 'Denied'),
        ('p', 'Pending Confirmation'),
        ('t', 'Contacted'),
        ('r', 'Follow-Up Required'),
        ('f', 'Followed-Up'),
        ('n', 'Not Contacted'),
        ('e', 'Dead Contact'),
    )
    
    def __unicode__(self):
        return '%s - %s' % (self.sponsor.name, self.event.name)
        
    sponsor = models.ForeignKey(Sponsor)
    event = models.ForeignKey('events.Event')
    status = models.CharField(max_length=1, choices=STATUS_TYPES, default='n')
    

class Prize(models.Model):
    # TODO: Add support for Tournaments.
    # TODO: Add image support.
    
    def __unicode__(self):
        return self.name
        
    def get_event_name(self):
      return self.eventsponsor.event.name
     
    def get_sponsor_name(self):
        return self.eventsponsor.sponsor.name
    
    get_event_name.short_description = 'Event Name'
    get_event_name.admin_order_field = 'eventsponsor__event__name'
    get_sponsor_name.short_description = 'Sponsor Name'

    eventsponsor = models.ForeignKey(EventSponsor, limit_choices_to={'status':'c', 'event__start_date__gte':datetime.now}, verbose_name="Sponsor/Event")
    name = models.CharField(max_length=100, verbose_name="Prize Name")
    description = models.TextField(blank=True)
    raffle_prize = models.BooleanField(default=False, verbose_name="Raffle Prize?")
    


    
    
