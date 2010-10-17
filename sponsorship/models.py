from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.auth.models import User

# class SponsorManager(models.Manager):
#     def get_query_set(self):
#         return super(SponsorManager, self).get_query_set().annotate(prizecount=models.Count('prize'))

class Sponsor(models.Model):
    # TODO: Add support for Events.
    
    def __unicode__(self):
        return self.name
        
    STATUS_TYPES = (
        ('c', 'Confirmed'),
        ('d', 'Denied'),
        ('p', 'Pending Confirmation'),
        ('t', 'Contacted'),
        ('r', 'Follow-Up Required'),
        ('f', 'Followed-Up'),
        ('n', 'Not Contacted'),
        ('d', 'Dead Contact'),
    )
    name = models.CharField(max_length=100, verbose_name="Sponsor Name")
    contact_name = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = PhoneNumberField(blank=True)
    status = models.CharField(max_length=1, choices=STATUS_TYPES, default='n')
    lan_rep = models.ForeignKey(User, verbose_name="LAN Representative")
    notes = models.TextField(blank=True)
    event = models.ManyToManyField('events.Event')
    # objects = SponsorManager()
    
    # def count(self):
    #     return self.prizecount
    # count.admin_order_field = 'prizecount'
    

class Prize(models.Model):
    # TODO: Add support for Tournaments.
    # TODO: Add image support.
    
    def __unicode__(self):
        return self.name
        
    event = models.ForeignKey('events.Event')
    sponsor = models.ForeignKey(Sponsor)
    name = models.CharField(max_length=100, verbose_name="Prize Name")
    description = models.TextField(blank=True)
    raffle_prize = models.BooleanField(verbose_name="Raffle Prize?")
    


    
    