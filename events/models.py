from django.db import models
from django.contrib.localflavor.us.models import USStateField
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.dispatch import receiver
from django.template import loader, Context
from django.core.mail import send_mail
# if we ever get rid of django-mailer change this
#from mailer import send_mail
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from paypal.standard.ipn.models import PayPalIPN
import uuid

class Event(models.Model):

    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=100, verbose_name='Event Name')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.ForeignKey('Venue')
    participant_limit = models.IntegerField()
    description = models.CharField(max_length=100)
    is_active = models.BooleanField()
    prepay_price = models.DecimalField(max_digits=4, decimal_places=2)
    atd_price = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='At-the-Door price')
    
    #participants = models.ManyToManyField('attendeereg.Attendee', blank=True)
    
class Venue(models.Model):
    
    def __unicode__(self):
        return self.name
        
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=30)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

class Participant(models.Model):
    
    def __unicode__(self):
        return '%s - %s' % (self.user.username, self.event)
    
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

class Coupon(models.Model):
    
    def __unicode__(self):
        return self.uuid
           
    def make_uuid():
        return str(uuid.uuid4())
    
    def activate(self):
        self.activated = True
        self.save()
        
    uuid = models.CharField(max_length=36, primary_key=True, default=make_uuid, editable=False)
    transaction = models.ForeignKey(PayPalIPN, blank=True, null=True, editable=False)
    activated = models.BooleanField()
    

class Ticket(models.Model):
    
    def __unicode__(self):
        return '%s - %s' % (self.participant.user.username, self.participant.event)

    participant = models.ForeignKey(Participant)
    #event = models.ForeignKey(Event)
    coupon = models.OneToOneField(Coupon, null=True)
    
@receiver(payment_was_successful)
def payment_complete(sender, **kwargs):
    # we do this so that the Coupon objects actually have their correct types
    coupons = [Coupon(transaction=sender) for i in xrange(sender.quantity)]
    for coupon in coupons:
        coupon.save()
    # I cannot see a better way to do this at the moment, so here we are
    # We pop the last coupon off the list to activate the ticket for the original payer
    participant = Participant.objects.get(id=sender.custom)
    coupon = coupons.pop()
    activate_coupon_and_ticket(participant, coupon)
    # We need to dispatch off an email...
    email_confirmation(participant=participant, coupons=coupons)

@receiver(payment_was_flagged)
def payment_flagged(sender, **kwargs):
    print sender
    print "Something went wrong..."
    
def activate_coupon_and_ticket(participant, coupon):
    ticket = Ticket(participant=participant, coupon=coupon)
    coupon.activate()
    ticket.save()
    
def email_confirmation(**kwargs):
    t = loader.get_template('events/email.txt')
    if 'participant' in kwargs:
        user = kwargs['participant'].user
        event = kwargs['participant'].event
        
    c = Context({
        'username': user.username,
        'event': event,
    })
    
    if len(kwargs['coupons']) > 0:
        c['coupons'] = kwargs['coupons']
    
    subj = '%s registration confirmation' % event.name
    fr = 'Big Shot Gaming <bigshot@bigshotgaming.com>'
    send_mail(subj, t.render(c), fr, ['tom@bigshotgaming.com'])
    
    
    
