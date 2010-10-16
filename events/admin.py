from django.contrib import admin
from events.models import Event
from events.models import Venue

class EventAdmin(admin.ModelAdmin):
    fields = (
        'name', 'description', 'start_date', 'end_date', 'venue',
        'participant_limit', 'contact_email', 'other_details'
    )
    
    list_display = ('name', 'start_date', 'end_date', 'venue')
    list_filter = ('venue',)
    search_fields= ('name',)
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
