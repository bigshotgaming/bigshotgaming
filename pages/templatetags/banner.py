from django import template
from sponsorship.models import Sponsor, EventSponsor

register = template.Library()

@register.inclusion_tag('/pages/banner.html')
def get_banner():
    sponsors = Sponsor.objects.filter(event=2, eventsponsor__status='c').exclude(banner=None)
    return sponsors