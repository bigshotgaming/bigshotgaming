from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from ticketing.models import Ticket
from ticketing.forms import TicketForm
from events.models import Event

@login_required
def ticket_signup(request):
    user = request.user
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            alias = form.cleaned_data['alias']
            byoc = form.cleaned_data['byoc']
            payment_type = form.cleaned_data['payment_type']
            t = Ticket(user=user, alias=alias, event=Event.objects.get(is_active=True), byoc=byoc, payment_type=payment_type)
            t.save()
            return HttpResponseRedirect('/registration/thanks/')
    else:
        form = TicketForm()

    c = {"form": form}
    c.update(csrf(request))
    return render_to_response('ticketing/index.html', c)
        
def thanks(request):
    pass
