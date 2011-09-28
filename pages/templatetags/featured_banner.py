import datetime
from django import template
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event
from sponsorship.models import Sponsor, EventSponsor

register = template.Library()

# yes, this is not DRY, but until Django 1.4, it needs to work

@register.inclusion_tag('pages/featured_banner.html')
def get_featured_banner():
    sponsors = Sponsor.objects.filter(featured_sponsor=True).exclude(featured_banner='')
    return {'sponsors': list(sponsors)}
