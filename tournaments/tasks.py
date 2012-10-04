import challonge
from django.conf import settings
from urllib2 import HTTPError
from celery import task

# this is here because it's a global that the challonge tasks require
challonge.set_credentials(settings.CHALLONGE_USERNAME, settings.CHALLONGE_API_KEY)

@task()
def create_tournament(name, url, tournament_type):
    challonge.tournaments.create(name=name, url=url, tournament_type=tournament_type)

@task()
def delete_tournament(tournament):
    challonge.tournaments.destroy(tournament=tournament)

@task()
def create_participant(tournament, team):
    challonge.participants.create(tournament=tournament.slugified_name, name=team.name)

@task()
def destroy_participant(tournament, team):
    try:
        for p in challonge.participants.index(tournament=tournament.slugified_name):
            if p['name'] == team.name:
                challonge.participants.destroy(tournament=tournament.slugified_name, participant_id=p['id'])
    except HTTPError, err:
        if err.code == 404:
            pass
        else:
            raise

@task()
def publish_and_start_tournament(tournament):
    challonge.tournaments.publish(tournament=tournament.slugified_name)
    challonge.tournaments.start(tournament=tournament.slugified_name)

