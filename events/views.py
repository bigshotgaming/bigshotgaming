from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from events.models import Event

def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except ObjectDoesNotExist:
        event = None
    return render_to_response('events/index.html', {'event':event}, context_instance=RequestContext(request))
