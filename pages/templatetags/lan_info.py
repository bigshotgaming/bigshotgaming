from django import template
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event

register = template.Library()

@register.inclusion_tag('pages/lan_info.html')
def lan_info():
    # this only supports one active event at a time
    try:
        event = Event.objects.get(is_active=True)
    except Event.DoesNotExist:
        event = None
    return {'event': event}

    
