from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from events.models import Event, Participant


class CarpoolOffer(models.Model):
    """A driver offering a ride to an event."""

    def __unicode__(self):
        return u"%s from %s, %s (%d seat(s) left)" % (
            self.driver.user.username,
            self.origin_city,
            self.origin_state,
            self.seats_remaining(),
        )

    driver = models.ForeignKey(Participant, related_name='carpool_offers')
    event = models.ForeignKey(Event)
    origin_city = models.CharField(max_length=100)
    origin_state = USStateField()
    total_seats = models.PositiveIntegerField(default=1, help_text="Number of seats available (not counting the driver)")
    notes = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, help_text="Public contact email (defaults to account email if blank)")
    created_time = models.DateTimeField(auto_now_add=True)

    def seats_remaining(self):
        return self.total_seats - self.riders.count()

    def is_full(self):
        return self.seats_remaining() <= 0

    class Meta:
        ordering = ['origin_state', 'origin_city']


class CarpoolRider(models.Model):
    """A participant who has claimed a seat in a carpool offer."""

    def __unicode__(self):
        return u"%s riding with %s" % (
            self.rider.user.username,
            self.offer.driver.user.username,
        )

    rider = models.ForeignKey(Participant, related_name='carpool_rides')
    offer = models.ForeignKey(CarpoolOffer, related_name='riders')
    joined_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rider', 'offer')
        ordering = ['joined_time']
