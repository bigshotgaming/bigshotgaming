from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from pooling.models import Car, Room
from events.models import Event, Participant


def index(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    return render(request, 'pooling/index.html', {
        'event': event,
    })

def cars(request):
    try:
        event = Event.objects.get(is_active=True)
    except (TypeError, ObjectDoesNotExist):
        event = None
    try:
        states = {}
        for car in Car.objects.get(event=event):
            if not car.state in states.keys:
                states[car.state] = car
            else
                states[car.state].append(car)
    return render(request, 'pooling/cars.htm', {
        'event': event,
        'states': states,
    })