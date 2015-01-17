from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from events.models import Participant
from paypal.standard.forms import PayPalPaymentsForm

class RegisterForm(forms.Form):
    payment_type = forms.ChoiceField(choices=(
        ('pp', 'Stripe'),
    ), widget=forms.RadioSelect)

    # we do this so that we can have the quantity field be a dropdown instead of a textbox
    ticket_quantity = forms.IntegerField(widget=forms.Select(choices=[(x,x) for x in range(1, 21)]))

    waiver = forms.BooleanField(
        error_messages={'required': 'You must accept the LAN waiver.'},
        label="Accept Waiver"
    )

class WaiverForm(forms.Form):
    waiver = forms.BooleanField(
        error_messages={'required': 'You must accept the LAN waiver.'},
        label="Accept Waiver"
    )