from seatmap.models import SeatMap, Seat, Table, STATUS_LIST
from events.models import Event, Participant, Coupon
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@login_required
def seatmap_display(request, event=None):
    if event is None:
        sm = SeatMap.objects.get(event=Event.objects.get(is_active=True))
    else:
        sm = SeatMap.objects.get(event=event)
    
    seats = Seat.objects.filter(seatmap=sm)
    for seat in seats:
        seat.status_full = seat.get_status_display()
       
    return render_to_response('seatmap/seatmap.html', {'tables':Table.objects.filter(seatmap=sm), 'seats':seats, 'seat_size':sm.seat_size, 'user':request.user})

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
       part = Participant.objects.get(user=request.user)
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