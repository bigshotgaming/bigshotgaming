from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

class JoinTeamForm(forms.Form):
    password = forms.CharField(max_length=10)

    # def clean(self):
    #     return True

class LeaveTeamForm(forms.Form):
    pass

class CreateTeamForm(forms.Form):
    name = forms.CharField(max_length=60)
    password = forms.CharField(max_length=10)

    # def clean(self):
    #     data = self.cleaned_data
    #     try:
    #         Team.objects.get()
    #     except:
    #         pass

