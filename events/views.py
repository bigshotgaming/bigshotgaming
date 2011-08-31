from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from events.models import Event, Participant
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
                request.session['participant'] = participant
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
    print request.session['qty']
    print request.session['participant']
    paypal_dict = {
        "business": "wiede1_1297892766_biz@cmich.edu",
        "amount": "15.00",
        "item_name": "thing",
        "invoice": uuid.uuid4(),
        "notify_url": "http://141.209.5.27/events/ppnotification",
        "return_url": "http://bsg.tomthebomb.net/registration/thanks/",
        "cancel_return": "http://bsg.tomthebomb.net/registration/thanks/",
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render_to_response("events/payment.html", context)
    
    
# def signup(request):
#     try:
#         event = Event.objects.get(is_active=True)
#     except ObjectDoesNotExist:
#         event = None
#     return render_to_response('events/signup.html', {'event':event}, context_instance=RequestContext(request))
    
    
