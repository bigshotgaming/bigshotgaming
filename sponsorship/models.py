from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.auth.models import User

class Sponsor(models.Model):
    # TODO: Add support for Events.
    
    def __unicode__(self):
        return self.name
        
    STATUS_TYPES = (
        ('CONF', 'Confirmed'),
        ('DENY', 'Denied'),
        ('PEND', 'Pending Confirmation'),
        ('CONT', 'Contacted'),
        ('FOLL', 'Followed-Up'),
        ('NOCO', 'Not Contacted'),
        ('DEAD', 'Dead Contact'),
    )
    name = models.CharField(max_length=100, verbose_name="Sponsor Name")
    contact_name = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = PhoneNumberField(blank=True)
    status = models.CharField(max_length=4, choices=STATUS_TYPES, default='NOCO')
    # will have to change this later
    lan_rep = models.ForeignKey(User, verbose_name="LAN Representative")
    notes = models.TextField(blank=True)
    

class Prize(models.Model):
    # TODO: Add support for Tournaments.
    # TODO: Add image support.
    
    def __unicode__(self):
        return self.name
        
    sponsor = models.ForeignKey(Sponsor)
    name = models.CharField(max_length=100, verbose_name="Prize Name")
    description = models.TextField(blank=True)

    
    