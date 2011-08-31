from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from events.models import Event, Participant, Coupon, Ticket, activate_coupon_and_ticket
from events.forms import RegisterForm
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
import uuid

def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except ObjectDoesNotExist:
        event = None
    return render_to_response('events/index.html', {'event':event}, context_instance=RequestContext(request))

@csrf_exempt
def register(request, eventid):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # we create a participant regardless of what people want to do
            participant = Participant.objects.get_or_create(user=request.user, event_id=eventid)[0]
            if form.cleaned_data['payment_type'] == 'pp':
                request.session['qty'] = form.cleaned_data['ticket_quantity']
                print eventid
                request.session['participant'] = participant.id
                print request.session['participant']
                return HttpResponseRedirect(reverse('events_payment'))   
            elif form.cleaned_data['payment_type'] == 'ad':
                print 'At-the-door payment detected'
                return HttpResponseRedirect('/durf/')
    else:
        form = RegisterForm()
        return render_to_response('events/register.html', {
            'form': form,
        })

def payment(request):
    # hm, not sure if this was the best idea
    # could do it the opposite way since it's easy to get the participant object
    event = Participant.objects.get(id=request.session['participant']).event
    print request.session['qty']
    paypal_dict = {
        "business": "wiede1_1297892766_biz@cmich.edu",
        "amount": event.prepay_price,
        "item_name": '%s ticket' % event.name,
        "invoice": uuid.uuid4(),
        "quantity": request.session['qty'],
        "custom": request.session['participant'],
        "notify_url": "http://141.209.5.37/events/ppnotification",
        "return_url": "http://bsg.tomthebomb.net/registration/thanks/",
        "cancel_return": "http://bsg.tomthebomb.net/registration/thanks/",
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render_to_response("events/payment.html", context)

@login_required    
def activate(request, eventid, uuid):
    # create a participant since these people will be signing up ONLY via coupon
    # if they were dumb enough to try and signup manually, this'll still catch em
    participant = Participant.objects.get_or_create(user=request.user, event_id=eventid)[0]
    coupon = Coupon.objects.get(uuid=uuid)
    activate_coupon_and_ticket(participant, coupon)
    return render_to_response('events/activated.html', {}, context_instance=RequestContext(request))
    
    
# def signup(request):
#     try:
#         event = Event.objects.get(is_active=True)
#     except ObjectDoesNotExist:
#         event = None
#     return render_to_response('events/signup.html', {'event':event}, context_instance=RequestContext(request))
    
    
