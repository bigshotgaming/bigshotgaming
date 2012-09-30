from django.db import models
from events.models import Event

class ScheduleItem(models.Model):

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event = models.ForeignKey(Event)

    class Meta:
        ordering = ['start_time']

