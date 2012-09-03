from django.db import models
from events.models import Event, Participant, Coupon
from sponsorship.models import Sponsor, Prize

PLATFORM_CHOICES = (('P','PC'),('C','Console'))
class Game(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    platform = models.CharField(max_length=1, choices=PLATFORM_CHOICES)

class Tournament(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    game = models.ForeignKey(Game)
    start_time = models.DateTimeField()
    event = models.ForeignKey(Event)
    # sponsors = models.ManyToMany(Sponsor)
    # prizes   = models.ManyToMany(Prize)
    teams = models.ManyToManyField('Team', blank=True)
    max_teams = models.IntegerField()

class Team(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    members = models.ManyToManyField(Participant, blank=True)
    password = models.CharField(max_length=10)