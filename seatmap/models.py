from django.db import models
from events.models import Event

class SeatMap(models.Model):
    event = models.OneToOne(Event)
    
    def __unicode(self)__:
        return 'Seatmap for %s' % self.event

class Table(models.Model):
    seatmap = models.ForeignKey(SeatMap)

    def __unicode(self)__:
        return 'Table in %s' % self.seatmap

STATUS_LIST = (('O','Open'),('T','Taken'),('A','Admin'))
class Seat(models.Model):
    table  = models.ForeignKey(Table)
    row    = models.SmallIntegerField()
    column = models.SmallIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_LIST)
    
    def __unicode(self)__:
        return 'Seat in %s' % self.table

