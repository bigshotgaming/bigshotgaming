from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard
from django.template import RequestContext
from django.http import HttpResponseRedirect
from events.models import Participant, Ticket

class RegisterForm1(forms.Form):
    registration_type = forms.ChoiceField(choices=(
        #('cc', 'Coupon Code Redemption'),
        ('tr', 'Ticket Registration'),
    ), widget=forms.RadioSelect)
    
class RegisterForm2(forms.Form):
    ticket_quantity = forms.IntegerField(min_value=1, max_value=100)

class RegisterForm3(forms.Form):
    payment_type = forms.ChoiceField(choices=(
        ('pp', 'PayPal'),
        ('pl', 'Pay later'),
        ('ad', 'Pay at-the-door'),
    ), widget=forms.RadioSelect)

class RegisterWizard(FormWizard):
    
    def parse_params(self, request, *args):
        self.eventid = args[0]
    
    def process_step(self, request, form, step):
        print request
        print self.eventid
        if step == 1:
            qty = form.cleaned_data['ticket_quantity']
            pass
        elif step == 2:
            if form.cleaned_data['payment_type'] == 'pp':
                print "PayPal detected"
            else:
                print form.cleaned_data['payment_type']

    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        try:
            participant = Participant.objects.get(user__username=request.user)
        except Participant.DoesNotExist:
            participant = Participant.objects.create(user__username=request.user)
            participant.save()
        ticket = Ticket.objects.create(event_id=self.eventid, participant=participant)
        ticket.save()

        return HttpResponseRedirect('/')
    
    
        
        
        # return render_to_response('events/done.html', {
        #     'form_data': [form.cleaned_data for form in form_list], 
        # }, context_instance=RequestContext(request))