from django.forms import ModelForm
from ticketing.models import Ticket

class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        exclude = ('user', 'event', 'seat', 'is_paid', 'paypal_id')
