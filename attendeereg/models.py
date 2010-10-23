from django.db import models
from django.contrib.auth.models import User
from django import forms
from events.models import Event

class Attendee(models.Model):
    def __unicode__(self):
        return self.user.username

    user = models.OneToOneField(User)
    events = models.ManyToManyField('events.Event', blank=True)

class SignupForm(forms.ModelForm):
    class Meta:
        model = Attendee
    
    #event = forms.ModelMultipleChoiceField(queryset=Attendee.objects.filter(event__name()))
    
    
