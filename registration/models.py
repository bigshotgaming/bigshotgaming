from django.db import models
from django.contrib.auth.models import User
from seatmap.models import Seat
from events.models import Event

PAYMENT_TYPES = (('O','Online'),('A','At The Door'))
class Ticket(models.Model):
    user         = models.OneToOne(User)
    alias        = models.CharField(max_length=100)
    seat         = models.ForeignKey(Seat, blank=True)
    byoc         = models.BooleanField(default=False, verbose_name='bringing own computer')
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPES)
    is_paid      = models.BooleanField(default=False)
    paypal_id    = models.CharField(max_length=50, blank=True, default=None, null=True)
