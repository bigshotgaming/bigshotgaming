from django.shortcuts import render
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from events.models import Event, Participant, Coupon, Waiver, activate_coupon
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
                # participant = Participant.objects.get_or_create(user=request.user, event_id=eventid)[0]
                if form.cleaned_data['payment_type'] == 'pp':
                    request.session['qty'] = form.cleaned_data['ticket_quantity']
                    return HttpResponseRedirect(reverse('events_payment'))   
                # elif form.cleaned_data['payment_type'] == 'ad':
                #     return HttpResponseRedirect('/events/thanks')
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
    event = Event.objects.get(is_active=True)
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": event.prepay_price,
        "item_name": '%s ticket' % event.name,
        "invoice": uuid.uuid4(),
        "quantity": request.session['qty'],
        "custom": request.user.username,
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
        try:
            activate_coupon(participant, coupon)
        except IntegrityError:
            return render(request, 'events/coupon_used.html', {
                'event':event
                })
        return render(request, 'events/activated.html', {
            'event':event
        })
    
def waiver(request, part_id):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    part = Participant.objects.get(id=part_id)
    return render_to_response('events/waiver_popup.html', {'waiver_form': WaiverForm(), 'part_id': part_id, 'username':part.user}, context_instance=RequestContext(request))

def waiver_sign(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)

    if request.method == "POST":
        p = Participant.objects.get(pk=request.POST['part_id'])
        w = Waiver(part=p, name=request.POST['name'])
        p.checkin_time = datetime.now()
        p.checked_in = True
        p.save()
        #s = Seat.objects.get(participant=p)
        #s.status = 'C'
        #s.save()
        if request.POST['pname']:
            w.pname = request.POST['pname']
            w.minor = True
            w.minor_age = request.POST['minor_age']
        w.save()
        #return render_to_response('events/waiver_okay.html', {'part': w.name})
        return HttpResponseRedirect('/seatmap/admin')
    return HttpResponse(status=444)    
    
