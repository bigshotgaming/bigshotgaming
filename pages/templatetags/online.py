from django import template
from django.core.cache import cache
from django.contrib.auth.models import User
from djangobb_forum.models import Category

register = template.Library()

@register.inclusion_tag('pages/online.html')
def online_users():
    #taken from djangobb_forum source
    users_cached = cache.get('users_online', {})
    users_online = users_cached and User.objects.filter(id__in = users_cached.keys()) or []
    guests_cached = cache.get('guests_online', {})
    return {'online_guests': guests_cached, 'online_members': users_online}
