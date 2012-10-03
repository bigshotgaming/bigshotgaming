from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from tournaments.models import Team, Tournament, team_full, password_correct, tournament_full

class JoinTeamForm(forms.Form):
    password = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team')
        self.tournament = kwargs.pop('tournament')
        super(JoinTeamForm, self).__init__(*args, **kwargs)

    def clean(self):
        # this is ugly and I promise I will fix it later
        if team_full(self.tournament, self.team):
            raise forms.ValidationError('This team is full.')
        if not password_correct(self.team, self.cleaned_data.get('password')):
            raise forms.ValidationError('That password is incorrect.')
        return self.cleaned_data

class LeaveTeamForm(forms.Form):
    pass

class CreateTeamForm(forms.Form):
    name = forms.CharField(max_length=60)
    password = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        super(CreateTeamForm, self).__init__(*args, **kwargs)

    def clean(self):
        if tournament_full(self.tournament):
            raise forms.ValidationError('Max teams for this tournament have been reached.')
        return self.cleaned_data

