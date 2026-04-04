import collections

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from schedule.models import ScheduleItem
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event


def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try:
        schedule = ScheduleItem.objects.filter(event=event).order_by('start_time')
    except Exception:
        schedule = None
    days = collections.OrderedDict()
    for item in schedule:
        if item.start_time.date() not in days:
            days[item.start_time.date()] = [item]
        else:
            days[item.start_time.date()].append(item)
    return render(request, 'schedule/index.html', {
        'event': event,
        'schedule': schedule,
        'days': days,
    })