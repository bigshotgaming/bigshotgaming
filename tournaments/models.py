from django.db import models
from events.models import Event
from sponsorship.models import Sponsor, Prize
#from registration.models import Ticket

PLATFORM_CHOICES = (('P','PC'),('C','Console'))
class Game(models.Model):
    name     = models.CharField(max_length=255)
    platform = models.CharField(max_length=1, choices=PLATFORM_CHOICES)

class Tournament(models.Model):
    name     = models.CharField(max_length=255)
    game     = models.ForeignKey(Game)
    when     = models.DateTimeField()
    event    = models.ForeignKey(Event)
    sponsors = models.ManyToMany(Sponsor)
    prizes   = models.ManyToMany(Prize)
    entrants = models.ManyToMany(Ticket)

class Team(models.Model):
    tournament = models.ForeignKey('TeamTournament')
    members    = models.ManyToMany(Ticket)

class TeamTournament(Tournament):
    entrants = models.ManyToMany(Team)
