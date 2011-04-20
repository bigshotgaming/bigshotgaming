import datetime
from django import template
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
        event = Event.objects.get(is_active=True)
    except ObjectDoesNotExist:
        event = Event.objects.filter(end_date__lte=datetime.datetime.now()).latest('end_date')
    sponsors = Sponsor.objects.filter(event=event, eventsponsor__status__in=['p', 'c', 'r', 'f']).exclude(banner='')
    return {'sponsor': list(sponsors)}
