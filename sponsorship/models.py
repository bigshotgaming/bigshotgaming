from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

class Sponsor(models.Model):
    STATUS_TYPES = (
        ('CONF', 'Confirmed'),
        ('DENY', 'Denied'),
        ('PEND', 'Pending Confirmation'),
        ('CONT', 'Contacted'),
        ('FOLL', 'Followed-Up'),
        ('NOCO', 'Not Contacted'),
    )
    company_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField()
    contact_phone = PhoneNumberField(blank=True)
    sponsor_status = models.CharField(max_length=4, choices=STATUS_TYPES, default='NOCO')
    # will have to change this later
    lan_rep = models.CharField(max_length=20)
    notes = models.TextField()

class Prize(models.Model):
    sponsor = models.ForeignKey(Sponsor)
    name = models.CharField(max_length=100)
    description = models.TextField()

    
    