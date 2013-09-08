import challonge, json
from django.conf import settings
from urllib2 import HTTPError
from celery import task
from threading import Timer

# this is here because it's a global that the challonge tasks require
challonge.set_credentials(settings.CHALLONGE_USERNAME, settings.CHALLONGE_API_KEY)

@task()
def create_tournament(name, url, tournament_type):
    try:
        challonge.tournaments.create(name=name, url=url, tournament_type=tournament_type)
    except Exception, e:
        print e

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

@task()
def automate_tournament(tournament):
    from tournaments.models import Tournament, Team
    from django.template import loader, Context
    from django.core.mail import send_mail
    tournament = Tournament.objects.get(id=tournament.id)
    if tournament.automated:
        tournament.automated_active = True
        # Look up the old match info
        try:
            info = json.loads(tournament.automated_data)
        except:
            info = { 'matches' : {}, 'emails' : {} }
        match_info = info.get('matches')
        email_info = info.get('emails')

        # email_info is a challonge_participant_id to email
        if email_info == {}:
            challonge_participants = challonge.participants.index(tournament.slugified_name)
            challonge_participants = dict([(p['name'], p['id']) for p in challonge_participants])
            tournament_teams = Team.objects.filter(tournament=tournament)
            for team in tournament_teams:
                email_info[str(challonge_participants[team.name])] = {
                    'email' : team.owner.user.email,
                    'name' : team.name
                }

        # See if there are new matches to be notified
        ct = challonge.matches.index(tournament.slugified_name)
        changed = False
        for match in ct:
            if match_info.get(str(match['id'])) == None:
                if match['player1-id'] != None and match['player2-id'] != None and match['state'] not in ['closed', 'complete']:
                    p1_info = email_info.get(str(match['player1-id']), {})
                    p2_info = email_info.get(str(match['player2-id']), {})
                    
                    t = loader.get_template('tournaments/match_notification.html')
                    if p1_info.get('email') not in ['', None]:
                        subject = "BSG Match Notification for %s" % tournament.name

                        c = Context({
                            'tournament' : tournament,
                            'opponent_name' : p2_info.get('name'),
                            'player_name' : p1_info.get('name')
                        })

                        fr = "Big Shot Gaming <bigshot@bigshotgaming.com>"

                        send_mail(subject, t.render(c), fr, [p1_info.get('email')])
                        print "Sending %s an email: %s" % (p1_info.get('name'), p1_info.get('email'))
                    if p2_info.get('email') not in ['', None]:
                        subject = "BSG Match Notification for %s" % tournament.name

                        c = Context({
                            'tournament' : tournament,
                            'opponent_name' : p1_info.get('name'),
                            'player_name' : p2_info.get('name')
                        })

                        fr = "Big Shot Gaming <bigshot@bigshotgaming.com>"

                        send_mail(subject, t.render(c), fr, [p2_info.get('email')]) 

                        print "Sending %s an email: %s" % (p2_info.get('name'), p2_info.get('email'))
                    match_info[match['id']] = 1
                elif match['state'] in ['closed', 'complete']:
                    print "Updating an already closed match."
                    match_info[match['id']] = 1
                changed = True
        if changed:
            if len(match_info.keys()) == len(ct):
                tournament.automated = False
                tournament.automated_active = False
                print "All matches have been reported."
            tournament.automated_data = json.dumps({ 'matches' : match_info, 'emails' : email_info })
            tournament.save()
        
        print 'automate_tournamant called.'
    
        t = Timer(5.0, automate_tournament, args=[tournament])
        t.start()
    else:
        tournament.automated_active = False
        tournament.save()
