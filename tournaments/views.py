from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from tournaments.models import Tournament, Team
from tournaments.forms import JoinTeamForm, LeaveTeamForm
from events.models import Event, Participant, Coupon


def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try: 
        tournaments_list = Tournament.objects.filter(event=event)
    except (TypeError, ObjectDoesNotExist):
        tournaments = None
    return render(request, 'tournaments/index.html', {
        'event': event,
        'tournaments_list': tournaments_list,
    })

def tournament(request, pk):
    tournament = Tournament.objects.get(pk=int(pk))
    teams = tournament.team_set.all()
    event = tournament.event
    return render(request, 'tournaments/tournament.html', {
        'event': event,
        'tournament': tournament,
        'teams': teams,
    })

def team(request, pk):

    team = Team.objects.get(pk=int(pk))
    tournament = team.tournament
    event = tournament.event
    participant = Participant.objects.get(user=request.user, event=event)
    on_team = False

    if participant in team.members.all():
        on_team = True

    # thanks to pwf for the following
    if request.method == 'POST':
        if not on_team:
            form = JoinTeamForm(request.POST)
            if form.is_valid():
                team.members.add(participant) 
                return HttpResponseRedirect(reverse('tournaments_team', args=[team.id]))   
        else:
            form = LeaveTeamForm(request.POST)
            if form.is_valid():
                team.members.remove(participant)
                return HttpResponseRedirect(reverse('tournaments_team', args=[team.id]))   
    else:
        form = JoinTeamForm

    return render(request, 'tournaments/team.html', {
        'event': event,
        'tournament': tournament,
        'team': team,
        'on_team': on_team,
        'form': form


    })
