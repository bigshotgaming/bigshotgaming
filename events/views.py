from django.shortcuts import render
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.conf import settings
from events.models import Event, Participant, Coupon, Waiver, activate_coupon, email_confirmation
from events.name_badge_pdf import NameBadgePDF
from events.forms import RegisterForm, WaiverForm
from paypal.standard.forms import PayPalPaymentsForm

import datetime
import uuid
import collections
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# TODO: Throw all this terrible code in a fucking fire where it will burn for all eternity.

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
        participants = Participant.objects.filter(event=event).order_by('signup_time')
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
                # this shit is fucking broken, that's what, what was I thinking
                if form.cleaned_data['payment_type'] == 'pp':
                    request.session['qty'] = form.cleaned_data['ticket_quantity']
                    return HttpResponseRedirect(reverse('events_payment'))   
                # elif form.cleaned_data['payment_type'] == 'ad':
                #     return HttpResponseRedirect('/events/thanks')

    else:
        # okay it turns out that NONE of this shit works if pay ATD is enabled, lol
        form = RegisterForm(initial={'payment_type':'pp'})
        # we do this here because we need a participant for the context
        # need to be able to check if they're paid or not
        # to render the template differently
        try: 
            participant = Participant.objects.get(user=request.user, event__id=eventid)
        except ObjectDoesNotExist:
            participant = None

        # hee haw, this is a way we can detect if someone bought multiple coupons
        if participant and participant.coupon:
            coupons = Coupon.objects.filter(stripe_transaction=participant.coupon.stripe_transaction).exclude(uuid=participant.coupon)
        else:
            coupons = None

        return render(request, 'events/register.html', {
            'event': Event.objects.get(id=eventid),
            'participant': participant,
            'coupons': coupons,
            'form': form,
            })
    return render(request, 'events/register.html', {
            'event': Event.objects.get(id=eventid),
            'form': form,
        })

@login_required
def payment(request):
    event = Event.objects.get(is_active=True)
    user = request.user
    quantity = request.session['qty']
    total_amount = quantity * event.prepay_price * 100
    if request.method == 'POST':
        token = request.POST['stripeToken']
        try:
            charge = stripe.Charge.create(
              amount=total_amount,
              currency="usd",
              card=token, # obtained with Stripe.js
              metadata={'user_email': user.email}
            )
        except stripe.CardError, e:
            return HttpResponseServerError('card failure detected')
        del request.session['qty']
        # we do this so that the Coupon objects actually have their correct types
        coupons = [Coupon(stripe_transaction=charge.id, event=event) for i in xrange(quantity)]
        for coupon in coupons:
            coupon.save()
        # I cannot see a better way to do this at the moment, so here we are
        # We pop the last coupon off the list to activate the ticket for the original payer
        participant = Participant.objects.get_or_create(user=user, event=event)[0]
        coupon = coupons.pop()
        activate_coupon(participant, coupon)
        # We need to dispatch off an email...
        email_confirmation(participant=participant, coupons=coupons)
        return HttpResponseRedirect(reverse('events_register', args=(event.id,))) 

    return render(request, "events/payment.html", {
        'data_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user': user,
        'quantity': quantity,
        'price': event.prepay_price,
        'total_amount': total_amount,
        
    })

@login_required    
def activate(request, eventid, uuid):
    # create a participant since these people will be signing up ONLY via coupon
    # if they were dumb enough to try and signup manually, this'll still catch em
    # This is all bastard code and it will never have a home or a family

    event = Event.objects.get(id=eventid)
    participant = Participant.objects.get_or_create(user=request.user, event=event)[0]
    if participant.coupon:
        return render(request, 'events/already_activated.html', {
            'event':event
        })

    if request.method == 'POST':
        form = WaiverForm(request.POST)
        if form.is_valid():
            print uuid
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
    else:
        form = WaiverForm()

    return render(request, 'events/activate.html', {
        'form': form,
        'event': event,
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

@login_required
def name_badges_pdf(request, event_id):
    if not request.user.is_staff:
        return HttpResponse('Not happenin', 403)

    try:
        event = Event.objects.get(id=event_id)
    except:
        return HttpResponse('Event with ID %s not found.' % event_id)
    participants = Participant.objects.filter(event__id=event_id)
    if len(participants) == 0:
        return HttpResponse('No participants found for event : ' + str(event_id))

    names = []
    for participant in participants:
        if participant.user.is_staff:
            names.append((participant.user.username, 'ADMIN'))
        else:
            names.append((participant.user.username, 'ATTENDEE'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s - Name Badges.pdf"' % event.name

    nbp = NameBadgePDF(response, event, names)
    nbp.save()

    return response

@login_required
def registration_history(request, event_id):

    # a fun exercise in date math for everybody involved

    event = Event.objects.get(id=event_id)
    participants = Participant.objects.filter(event=event).order_by('signup_time')
    data = {}
    last_count = 0

    # figuring out our boundaries
    # the 120 day limit is arbitrary
    start_date = int((event.start_date - datetime.timedelta(days=120)).date().strftime('%s'))*1000
    end_date = int(event.end_date.date().strftime('%s'))*1000

    for participant in participants:
        key = int((participant.signup_time.date().strftime('%s')))*1000
        # we're checking to see if somebody signed up before our above cutoff
        # if they signup before that cutoff, it just adds their count to the start_date
        if key > start_date:
            if key in data:
                data[key] += 1
            else:
                data[key] = last_count+1
            last_count = data[key]
        else:
            if start_date in data:
                data[start_date] += 1
            else:
                data[start_date] = 0

    # here we're checking to see if we're looking at this data before the fact or after
    # we want the graph to cutoff on today if it's before the LAN ends
    now = int(datetime.datetime.now().date().strftime('%s'))*1000
    if int(datetime.datetime.now().date().strftime('%s'))*1000 > end_date:
        data[end_date] = last_count
    else:
        if now in data:
            pass
        else:
            data[now] = last_count

    # time to sort our dict
    data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))

    tooltip_date = "%d %b %Y"
    extra_serie = {"tooltip": {"y_start": "", "y_end": " participants"},
                   "date_format": tooltip_date}
    chartdata = {'x': data.keys(),
                 'name1': 'Signup Count', 'y1': data.values(), 'extra1': extra_serie,
                }

    charttype = "lineChart"
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'date_tag' : True,
    }
    return render(request, 'events/linechart.html', data)
    #return render_to_response('linechart.html', data)


