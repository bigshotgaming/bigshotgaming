from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard
from django.template import RequestContext
from django.http import HttpResponseRedirect
from events.models import Participant, Ticket

class RegisterForm1(forms.Form):
    payment_type = forms.ChoiceField(choices=(
        ('pp', 'PayPal'),
        ('ad', 'Pay at-the-door'),
    ), widget=forms.RadioSelect)
    
class RegisterForm2(forms.Form):
    ticket_quantity = forms.IntegerField(min_value=1, max_value=10)


class RegisterWizard(FormWizard):
    
    def parse_params(self, request, *args):
        self.eventid = args[0]
    
    def process_step(self, request, form, step):
        #print request
        print self.eventid
        #print form.cleaned_data
        if step == 0:
            participant = Participant.objects.get_or_create(user=request.user, event_id=self.eventid)[0]
            print form.cleaned_data
            if form.cleaned_data['payment_type'] == 'pp':
                print "PayPal detected"
            elif form.cleaned_data['payment_type'] == 'ad':
                print "At-the-door payment"
                del self.form_list[1]
        elif step == 2:
            qty = form.cleaned_data['ticket_quantity']

    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        #ticket = Ticket.objects.create(event_id=self.eventid, participant=participant)
        #ticket.save()

        return HttpResponseRedirect('/')
    
    
        
        
        # return render_to_response('events/done.html', {
        #     'form_data': [form.cleaned_data for form in form_list], 
        # }, context_instance=RequestContext(request))