from seatmap.models import SeatMap, Seat, Table, STATUS_LIST
from events.models import Event, Participant, Coupon
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from datetime import datetime
import json

@csrf_exempt
def seatmap_data(request):
    seatmap_data = {}

    seatmap_id = request.GET.get('seatmap_id')
    seatmap = SeatMap.objects.filter(id=seatmap_id)
    if len(seatmap) != 1:
        return HttpResponseBadRequest('SeatMap with ID "%s" does not exitst.' % seatmap_id)
    seatmap = seatmap[0]
    
    objects = list(Seat.objects.filter(seatmap=seatmap)) + list(Table.objects.filter(seatmap=seatmap))
    seatmap_data = serializers.serialize('json', objects, use_natural_keys=True)
    return HttpResponse(seatmap_data, content_type='application/json', status=200)

def seatmap_display(request, event=None):
    if event is None:
        sm = SeatMap.objects.get(event=Event.objects.get(is_active=True))
    else:
        sm = SeatMap.objects.get(event=event)
    
    seats = Seat.objects.filter(seatmap=sm)
    for seat in seats:
        seat.status_full = seat.get_status_display()
       
    return render(request, 'seatmap/seatmap_page.html', {})

@csrf_exempt
@login_required
def seat_display(request, seat, event=None):
    if event is None:
        event = Event.objects.get(is_active=True)
    try:
        seat = Seat.objects.get(pk=seat)
    except Seat.DoesNotExist:
        return HttpResponse('Seat not found', status=404)
    
    try:
       part = Participant.objects.get(user=request.user, event=event)
       coup = part.coupon
    except (Participant.DoesNotExist, Coupon.DoesNotExist):
       return HttpResponse('notpaid')

    try:
       sss = Seat.objects.get(participant=part)  
       return HttpResponse('already')
    except Seat.DoesNotExist:
       pass
    
    if seat.status != 'O' or seat.seatmap.event.is_active == False:
        return HttpResponse('Seat Not Open. Status: %s' % seat.status, status=422)
       
    if coup == None:
        return HttpResponse('User not paid')
    
    paid = coup.activated
    
    if  request.method == "POST":
        seat.status = 'T'
        seat.participant = part
        seat.save()
        return HttpResponse('success')
    else:
        return HttpResponse('confirm')

@login_required
def seatmap_admin(request, event=None):
    if not request.user.is_staff:
        return HttpResponse('GTFO NOOBLORD', 403)

    if event is None:
        sm = SeatMap.objects.get(event=Event.objects.get(is_active=True))
    else:
        sm = SeatMap.objects.get(event=event)

    seats = Seat.objects.filter(seatmap=sm)
    for seat in seats:
        seat.status_full = seat.get_status_display()

    return render_to_response('seatmap/seatmap_admin.html', {'tables':Table.objects.filter(seatmap=sm), 'seats':seats, 'seat_size':sm.seat_size})

@csrf_exempt
@login_required
def seat_admin(request, seat):
    try:
        seat = Seat.objects.get(pk=seat)
    except Seat.DoesNotExist:
        return HttpResponse('Seat not found', status=404)
    
    if request.method == 'POST':
        seat.x = request.POST['x-edit']
        seat.y = request.POST['y-edit']
        seat.status = request.POST['status-edit']
        if request.POST['part-edit'] == '':
            seat.participant = None
        else:
            seat.participant = Participant.objects.get(pk=request.POST['part-edit'])
        seat.save()
        return HttpResponse('success')
    elif request.method == 'DELETE':
        seat.delete()
        return HttpResponse('success')
    elif request.method == 'PUT':
        seat.status = 'C'
        seat.save()
        seat.participant.checked_in = True
        seat.participant.checkin_time = datetime.now()
        seat.participant.save()
        return HttpResponse('success')
    else:
        parts = Participant.objects.filter(event=seat.seatmap.event)
        return render_to_response('seatmap/seat_admin.html', {'seat':seat, 'parts':parts, 'statuses':STATUS_LIST})
        
@csrf_exempt
@login_required
def seat_create(request):
    Seat.objects.create(seatmap=SeatMap.objects.get(event=Event.objects.get(is_active=True)), x=request.POST['x-create'], y=request.POST['y-create'], status='O', participant=None).save()
    return HttpResponse('success')

@csrf_exempt
@login_required
def table_create(request):
    sm = SeatMap.objects.get(event=Event.objects.get(is_active=True))
    ss = sm.seat_size
    w = int(request.POST['w-create']) * ss
    h = int(request.POST['h-create']) * ss
    print w, h
    Table.objects.create(seatmap=sm, name=request.POST['name-create'], x=request.POST['x-create'], y=request.POST['y-create'], w=w, h=h).save()
    return HttpResponse('success')

@csrf_exempt
@login_required
def seatmap_save(request):
    if request.POST.get('seat_data'):
        data = json.loads(request.POST.get('seat_data'))
        seatmap_id = request.POST.get('seatmap_id')
        seatmap = SeatMap.objects.get(id=seatmap_id)
        Seat.objects.filter(seatmap=seatmap).delete()
        for seat in data:
            print seat
            s = Seat()
            s.seatmap = seatmap
            s.x = seat['x']
            s.y = seat['y']
            s.status = seat['status']
            if seat.get('participant') not in [None, 'null', 'None']:
                p = Participant.objects.filter(event=seatmap.event, user__username=seat['participant'])
                if len(p) == 0:
                    p = Participant()
                    p.event = seatmap.event
                    u = User.objects.get(username = seat['participant'])
                    p.user = u
                    p.save()
                else:
                    p = p[0]
                s.participant = p;
            s.save()
    return HttpResponse('success')

@csrf_exempt
@login_required
def seatmap_user(request):
    if request.GET.get('q'):
        users = User.objects.filter(username__contains=request.GET.get('q'))
        return HttpResponse(json.dumps([user.username for user in users]), content_type='application/json', status=200)
    return HttpResponseBadRequest('fail')
    
@csrf_exempt
@login_required
def seatmap_sitdown(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('log in to sit down')
    if None in [request.POST.get('x'), request.POST.get('y'), request.POST.get('seatmap_id')]:
        print 
        return HttpResponseBadRequest('missing a variable in the query string: ' + str([request.POST.get('x'), request.POST.get('y'), request.POST.get('seatmap_id')]))
    seat = Seat.objects.filter(x=request.POST.get('x'), y=request.POST.get('y'), seatmap__id=request.POST.get('seatmap_id'))
    if len(seat) != 1:
        return HttpResponseBadRequest('seat not found')
    seat = seat[0]
    seatmap = SeatMap.objects.get(id=request.POST.get('seatmap_id'))
    try:
        p = Participant.objects.get(event=seatmap.event, user=request.user)
    except Participant.DoesNotExist:
        return HttpResponseForbidden('no participant found for this user')
    else:
        if seat.participant != None and seat.participant != p:
            return HttpResponseBadRequest('participant already sitting here')
        if p.seat_set.count() != 0:
            return HttpResponseBadRequest('participant already has a seat')
        else:
            seat.participant = p
            seat.status = 'C'
            seat.save()
            return HttpResponse('good')
    
