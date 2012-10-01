from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from tournaments.models import Tournament, Team
from tournaments.forms import JoinTeamForm, LeaveTeamForm, CreateTeamForm
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
    # ugly temporary hacks here
    form = None
    participant = None
    try:
        participant = Participant.objects.get(user=request.user, event=event)
        if request.method == 'POST':
            form = CreateTeamForm(request.POST, tournament=tournament)
            if form.is_valid():
                try:
                    ct = Team.objects.get(members=participant, tournament=tournament)
                    ct.members.remove(participant)
                except:
                    pass
                team = Team.objects.create(name=form.cleaned_data['name'], password=form.cleaned_data['password'],
                    tournament=tournament)
                team.members.add(participant)
                return HttpResponseRedirect(reverse('tournaments_tournament', args=[tournament.id]))
        else:
            form = CreateTeamForm(tournament=tournament)
    except (TypeError, ObjectDoesNotExist):
        pass

    return render(request, 'tournaments/tournament.html', {
        'event': event,
        'tournament': tournament,
        'teams': teams,
        'form': form,
        'participant': participant,
    })

def team(request, pk):

    team = Team.objects.get(pk=int(pk))
    tournament = team.tournament
    event = tournament.event

    #more ugly hacks here
    form = None
    participant = None
    on_team = False
    try:
        participant = Participant.objects.get(user=request.user, event=event)



        if participant in team.members.all():
            on_team = True

        # thanks to pwf for the following
        if request.method == 'POST':
            if not on_team:
                form = JoinTeamForm(request.POST, team=team, tournament=tournament)
                if form.is_valid():
                    team.members.add(participant) 
                    return HttpResponseRedirect(reverse('tournaments_team', args=[team.id]))   
            else:
                form = LeaveTeamForm(request.POST)
                if form.is_valid():
                    team.members.remove(participant)
                    return HttpResponseRedirect(reverse('tournaments_team', args=[team.id]))   
        else:
            form = JoinTeamForm(team=team, tournament=tournament)
    except (TypeError, ObjectDoesNotExist):
        pass

    return render(request, 'tournaments/team.html', {
        'event': event,
        'tournament': tournament,
        'team': team,
        'on_team': on_team,
        'form': form


    })
