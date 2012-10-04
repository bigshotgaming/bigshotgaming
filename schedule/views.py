from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from schedule.models import ScheduleItem
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event


def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try:
        schedule = ScheduleItem.objects.filter(event=event)
    except:
        schedule = None
    # days = {}
    #     for item in schedule:
    #         if item.start_time.day is not in days:
    #             days[start_time.day] = [item,]
    #         else
    #             days[start_time.day].append(item)
    #     print days
    return render(request, 'schedule/index.html', {
        'event': event,
        'schedule': schedule,
    })