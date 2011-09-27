from django.db import models
from events.models import Event, Participant

class SeatMap(models.Model):
    event = models.OneToOneField(Event)
    seat_size = models.SmallIntegerField()
    
    def __unicode__(self):
        return 'Seatmap for %s' % self.event

STATUS_LIST = (('O','Open'),('T','Taken'),('A','Admin'),('N', 'None'))
class Seat(models.Model):
    seatmap = models.ForeignKey(SeatMap)
    x = models.SmallIntegerField()
    y = models.SmallIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_LIST)
    participant = models.ForeignKey(Participant, blank=True, null=True)
    
    def __unicode__(self):
        return 'Seat at (%d, %d): %s' % (self.x, self.y, self.status)
        
class Table(models.Model):
    seatmap = models.ForeignKey(SeatMap)
    x = models.SmallIntegerField()
    y = models.SmallIntegerField()
    w = models.SmallIntegerField(default=160)
    h = models.SmallIntegerField(default=80)
    name = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return 'Table %s' % self.name