from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from events.models import Event, Participant, Coupon, activate_coupon
from events.forms import RegisterForm
from paypal.standard.forms import PayPalPaymentsForm

import uuid

def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try:
        participant = Participant.objects.get(user=request.user, event=event)
    except (TypeError, ObjectDoesNotExist):
        participant = None
    
    return render(request, 'events/index.html', {
        'event':event,
        'participant':participant,
    })

def participants(request, eventid):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try:
        participants = Participant.objects.filter(event=event)
    except (TypeError, ObjectDoesNotExist):
        participants = None
    
    return render(request, 'events/participants.html', {
        'participants':participants,
    })

@login_required
def register(request, eventid):
    # we need to add a bit of validation here
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # we need to break out if the event is full
            event = Event.objects.get(is_active=True)
            if event.number_remaining() <= 0:
                # and I need to make this better later
                return HttpResponseRedirect('/events/full')
            else:
                # we create a participant regardless of what people want to do
                participant = Participant.objects.get_or_create(user=request.user, event_id=eventid)[0]
                if form.cleaned_data['payment_type'] == 'pp':
                    request.session['qty'] = form.cleaned_data['ticket_quantity']
                    request.session['participant'] = participant.id
                    return HttpResponseRedirect(reverse('events_payment'))   
                elif form.cleaned_data['payment_type'] == 'ad':
                    return HttpResponseRedirect('/events/thanks')
    else:
        form = RegisterForm()
        # we do this here because we need a participant for the context
        # need to be able to check if they're paid or not
        # to render the template differently
        try: 
            participant = Participant.objects.get(user=request.user, event__id=eventid)
        except ObjectDoesNotExist:
            participant = None
            
        return render(request, 'events/register.html', {
            'event': Event.objects.get(id=eventid),
            'participant': participant,
            'form': form,
        })

@login_required
def payment(request):
    # hm, not sure if this was the best idea
    # could do it the opposite way since it's easy to get the participant object
    event = Participant.objects.get(id=request.session['participant']).event
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": event.prepay_price,
        "item_name": '%s ticket' % event.name,
        "invoice": uuid.uuid4(),
        "quantity": request.session['qty'],
        "custom": request.session['participant'],
        "notify_url": "http://www.bigshotgaming.com/events/ppnotification",
        "return_url": "http://www.bigshotgaming.com/events/thanks",
        "cancel_return": "http://www.bigshotgaming.com",
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "events/payment.html", {
        "form": form,
    })

@login_required    
def activate(request, eventid, uuid):
    # create a participant since these people will be signing up ONLY via coupon
    # if they were dumb enough to try and signup manually, this'll still catch em
    event = Event.objects.get(id=eventid)
    participant = Participant.objects.get_or_create(user=request.user, event=event)[0]
    if participant.coupon:
        return render(request, 'events/already_activated.html', {
            'event':event
        })
    else:
        coupon = Coupon.objects.get(uuid=uuid)
        activate_coupon(participant, coupon)
        return render(request, 'events/activated.html', {
            'event':event
        })
    
    
    
