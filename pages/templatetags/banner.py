import datetime
from django import template
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event
from sponsorship.models import Sponsor, EventSponsor

register = template.Library()

@register.inclusion_tag('pages/banner.html')
def get_banner():
    '''
    blatantly stolen from the sponsors view
    '''
    try:
        # thanks to avidal for the below
        event = Event.objects.filter(Q(is_active=True) | Q(end_date__lte=datetime.datetime.now())).order_by('-is_active', '-end_date')[0]
    except IndexError:
        # we do this so that if no events are returned, the below code does not throw an exception
        event = None
    sponsors = Sponsor.objects.filter(event=event, eventsponsor__status__in=['p', 'c', 'r', 'f']).exclude(banner='')
    return {'sponsors': list(sponsors)}
