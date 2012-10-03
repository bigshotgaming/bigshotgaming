import challonge
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from events.models import Event, Participant, Coupon
from sponsorship.models import Sponsor, Prize

PLATFORM_CHOICES = (('P','PC'),('C','Console'))


class Game(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    platform = models.CharField(max_length=1, choices=PLATFORM_CHOICES)

class Tournament(models.Model):
    STYLE_CHOICES = (
        ('S', 'Single Elimination'),
        ('D', 'Double Elimination'),
        ('R', 'Round Robin'),
        ('W', 'Swiss'),
    )
    def __unicode__(self):
        return self.name

    # thanks to dittoed for the following
    def save(self, *args, **kwargs):
        self.slugified_name = slugify("%s %s" % (self.event.name, self.name)).replace("-", "_")
        return super(Tournament, self).save(*args, **kwargs)

    def get_tournament_style(self):
        style = None
        for choice in self.STYLE_CHOICES:
            if self.style == choice[0]:
                style = choice[1]
                return style

    name = models.CharField(max_length=60)
    game = models.ForeignKey(Game)
    event = models.ForeignKey(Event)
    # sponsors = models.ManyToMany(Sponsor)
    # prizes   = models.ManyToMany(Prize)
    team_size = models.IntegerField()
    max_teams = models.IntegerField()
    rules = models.TextField()
    style = models.CharField(max_length=1, choices=STYLE_CHOICES)
    slugified_name = models.SlugField(editable=False)
    is_active = models.BooleanField(default=True)
    has_started = models.BooleanField()

class Team(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    members = models.ManyToManyField(Participant, blank=True)
    password = models.CharField(max_length=10)
    tournament = models.ForeignKey(Tournament)

def team_full(tournament, team):
    if team.members.count() >= tournament.team_size:
        return True

def tournament_full(tournament):
    if tournament.team_set.count() >= tournament.max_teams:
        return True

def password_correct(team, password):
    if password == team.password:
        return True

def _challonge_auth():
    challonge.set_credentials(settings.CHALLONGE_USERNAME, settings.CHALLONGE_API_KEY)

@receiver(post_save, sender=Tournament)
def create_challonge_tournament(sender, **kwargs):
    tournament = kwargs['instance']
    _challonge_auth()
    tournament_style = tournament.get_tournament_style().lower()
    tournament_name = "%s - %s" % (tournament.event.name, tournament.name)
    if kwargs['created']:
        challonge.tournaments.create(name=tournament_name, url=tournament.slugified_name, tournament_type=tournament_style)

@receiver(pre_delete, sender=Tournament)
def delete_challonge_tournament(sender, **kwargs):
    tournament = kwargs['instance']
    _challonge_auth()
    challonge.tournaments.destroy(tournament=tournament.slugified_name)

@receiver(post_save, sender=Team)
def create_challonge_team(sender, **kwargs):
    team = kwargs['instance']
    tournament = kwargs['instance'].tournament
    _challonge_auth()
    challonge.participants.create(tournament=tournament.slugified_name, name=team)

@receiver(pre_delete, sender=Team)
def delete_challonge_team(sender, **kwargs):
    team = kwargs['instance']
    tournament = team.tournament
    _challonge_auth()
    for p in challonge.participants.index(tournament=tournament.slugified_name):
        if p['name'] == team.name:
            challonge.participants.destroy(tournament=tournament.slugified_name, participant_id=p['id'])

    