from django.db import models
from events.models import Event, Participant

class Car(models.Model):
    def __unicode__(self):
        return self.part + ' driving from ' + self.city + ', ' + self.state

    event = models.ForeignKey(Event)
    part = models.ForeignKey(Participant) # driver
    city = models.CharField(max_length=200) # city they're leaving
    state = models.CharField(max_length=2) # state they're leaving (or Michigan)
    contact = models.CharField(max_length=200) # how to contact them, probably an email address (maybe phone number?)
    spots = models.SmallIntegerField() # how many people can go with them

class Room(models.Model):
    def __unicode__(self):
        return self.part + ' staying at ' + self.name

    event = models.ForeignKey(Event)
    part = models.ForeignKey(Participant)  # renter (assuming hotel rooms or maybe apartments)
    name = models.CharField(max_length=200) # name of the place they're staying
    contact = models.CharField(max_length=200) # how to contact them, probably an email address (maybe phone number?)
    spots = models.SmallIntegerField() # how many people can go with them