from django.db import models
from django.core.mail import send_mail
from django.contrib.localflavor.us.models import USStateField
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader, Context
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from paypal.standard.ipn.models import PayPalIPN
import uuid
import datetime

class Event(models.Model):

    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=100, verbose_name='Event Name')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.ForeignKey('Venue')
    description = models.TextField()
    is_active = models.BooleanField()
    reg_enabled = models.BooleanField()
    waiver = models.FileField(upload_to='events/waivers/', blank=True)

    def total_tickets(self):
        for ttype in self.tickettype_set:
            print 'butts'
            print ttype.max_available
        return 0
        # return self.tickettype_set.max_available
    
class Venue(models.Model):
    
    def __unicode__(self):
        return self.name
        
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=30)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

class ParticipantManager(models.Manager):
    def get_by_natural_key(self, user, event):
        return self.get(user=user.username, event=event.name)

class Participant(models.Model):
    
    def __unicode__(self):
        return '%s - %s' % (self.user.username, self.event)

    def natural_key(self):
        return (self.user.username, self.event.name)
    
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    ticket = models.ForeignKey('Ticket', blank=True, null=True)
    signup_time = models.DateTimeField(auto_now_add=True)
    checked_in = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(blank=True, null=True)

class Ticket(models.Model):
    def __unicode__(self):
        return self.uuid

    def create_uuid():
        return str(uuid.uuid4())

    uuid = models.CharField(max_length=36, primary_key=True, default=create_uuid, editable=False)
    tickettype = models.ForeignKey('TicketType')
    transaction = models.ForeignKey('Transaction', blank=True, null=True)
    notes = models.TextField()

    # def __unicode__(self):
    #     return self.uuid

class TicketType(models.Model):

    # We do this because we use these constants in other applications
    SPECTATOR = 'S'
    CONSOLE = 'C'
    BYOC = 'B'

    CATEGORY_CHOICES = (
        (SPECTATOR, 'Spectator'),
        (CONSOLE, 'Console'),
        (BYOC, 'BYOC'),
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    max_available = models.IntegerField()
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    event = models.ForeignKey(Event)
    
    def __unicode__(self):
        return self.name

    def tickets_available(self):
        return self.max_available - self.ticket_set.count()

class Transaction(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    external_transaction = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return (self.user + self.external_transaction)

class Waiver(models.Model):
    def __unicode__(self):
        return '%s\'s waiver signed %s' % (self.part.user.username, self.signed_on)

    part = models.ForeignKey(Participant)
    name = models.CharField(max_length=255)
    pname = models.CharField(max_length=255, blank=True, null=True)
    minor = models.BooleanField()
    minor_age = models.IntegerField(max_length=2, blank=True, null=True)
    signed_on = models.DateTimeField(auto_now_add=True)







# class Coupon(models.Model):
    
#     def __unicode__(self):
#         return self.uuid
           
#     def make_uuid():
#         return str(uuid.uuid4())
    
#     def activate(self):
#         self.activated = True
#         self.activated_time = datetime.datetime.now()
#         self.save()
        
#     uuid = models.CharField(max_length=36, primary_key=True, default=make_uuid, editable=False)
#     event = models.ForeignKey(Event)
#     transaction = models.ForeignKey(PayPalIPN, blank=True, null=True, editable=False)
#     activated = models.BooleanField()
#     created_time = models.DateTimeField(auto_now_add=True)
#     activated_time = models.DateTimeField(null=True, blank=True)
#     notes = models.TextField(blank=True)

# @receiver(post_save, sender=Event)
# def one_active(sender, **kwargs):
#     instance = kwargs['instance']
#     if instance.is_active is True:
#         Event.objects.exclude(pk=instance.pk).update(is_active=False)
    
# @receiver(payment_was_successful)
# def payment_complete(sender, **kwargs):
#     user = User.objects.get(username=sender.custom)
#     event = Event.objects.get(is_active=True)
#     # we do this so that the Coupon objects actually have their correct types
#     coupons = [Coupon(transaction=sender, event=event) for i in xrange(sender.quantity)]
#     for coupon in coupons:
#         coupon.save()
#     # I cannot see a better way to do this at the moment, so here we are
#     # We pop the last coupon off the list to activate the ticket for the original payer
#     participant = Participant.objects.get_or_create(user=user, event=event)[0]
#     coupon = coupons.pop()
#     activate_coupon(participant, coupon)
#     # We need to dispatch off an email...
#     email_confirmation(participant=participant, coupons=coupons)

# @receiver(payment_was_flagged)
# def payment_flagged(sender, **kwargs):
#     print sender
#     print "Something went wrong..."
    
# def activate_coupon(participant, coupon):
#     participant.coupon = coupon
#     coupon.activate()
#     participant.save()
    
# def email_confirmation(**kwargs):
#     t = loader.get_template('events/email.txt')
#     if 'participant' in kwargs:
#         user = kwargs['participant'].user
#         event = kwargs['participant'].event
        
#     c = Context({
#         'username': user.username,
#         'event': event,
#     })
    
#     if len(kwargs['coupons']) > 0:
#         c['coupons'] = kwargs['coupons']
    
#     subj = '%s registration confirmation' % event.name
#     fr = 'Big Shot Gaming <bigshot@bigshotgaming.com>'
#     send_mail(subj, t.render(c), fr, [user.email])
    
    
    
