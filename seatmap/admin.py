from seatmap.models import SeatMap, Seat, Table
from events.models import Event
from django.contrib import admin
from django.shortcuts import render_to_response
from django.http import Http404
from django.shortcuts import get_object_or_404

def seatmap_display(request, sm=None):
    size = 30 if sm is None else sm.size
    
    y = {}
    
    for yy in range(30):
        x_ = {}
        for xx in range(30):
            x_[xx] = None
        y[yy] = x_
    
    for seat in Seat.objects.all():
        for xx in y[seat.row]:
            if xx == seat.column:
                y[seat.row].update({seat.column: seat})
    
    return render_to_response('seatmap/seatmap.html', {'grid':y})
    
def seat_display(request, x, y):
    seat = None
    try:
        seat = get_object_or_404(Seat, row=y, column=x)
    except Seat.DoesNotExist:
        raise Http404
    
    try:
        user = seat.ticket
    except all:
        user = None
    
    
    return render_to_response('seatmap/seat.html', {'seat':seat, 'user':user, 'status':seat.get_status_display()})

admin.site.register(SeatMap)
admin.site.register(Seat)
admin.site.register(Table)
