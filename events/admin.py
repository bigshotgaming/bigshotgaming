from django.contrib import admin
from events.models import Event
from events.models import Venue

class EventAdmin(admin.ModelAdmin):
    fields = (
        'name', 'start_date', 'end_date', 'venue',
        'participant_limit', 'description', 'is_active',
    )
    
    list_display = ('name', 'start_date', 'end_date', 'venue',
        'participant_limit', 'is_active'
    )
    
    list_filter = ('venue',)
    search_fields= ('name',)
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
