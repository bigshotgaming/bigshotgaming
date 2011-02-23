from django.db import models
from events.models import Event

class SeatMap(models.Model):
    event = models.OneToOneField(Event)
    size = models.SmallIntegerField()
    
    def __unicode__(self):
        return 'Seatmap for %s' % self.event

class Row(models.Model):
    seatmap = models.ForeignKey(SeatMap)
    row = models.SmallIntegerField()

    def __unicode__(self):
        return 'Row %d in %s' % (self.row, self.seatmap)

STATUS_LIST = (('O','Open'),('T','Taken'),('A','Admin'),('N', 'None'))
class Seat(models.Model):
    row = models.SmallIntegerField()
    column = models.SmallIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_LIST)
    
    def __unicode__(self):
        return 'Seat %d at %s' % (self.column, self.row)