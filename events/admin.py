from django.http import HttpResponse
from django.contrib import admin
from events.models import Event, Venue, Participant, Ticket, TicketType, Transaction

def mark_as_paid(modeladmin, request, queryset):
    pass
    # for participant in queryset:
    #     participant.coupon = Coupon(event=Event.objects.get(is_active=True))
    #     participant.coupon.activate()
    #     participant.save()
mark_as_paid.short_description = "Mark selected participants as paid"

class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('signup_time',)
    list_display = ('user', 'event', 'signup_time', 'checkin_time',)
    list_filter = ('event', 'checked_in')
    search_fields = ['user__username']
    actions = [mark_as_paid]
    
    def user_has_seat(self, obj):
        if obj.seat_set.all():
            return True
        else:
            return False
    user_has_seat.short_description = "Has seat?"
    user_has_seat.boolean = True
    
class EventAdmin(admin.ModelAdmin):
    fields = (
        'name', 'start_date', 'end_date', 'venue',
        'description', 'is_active', 'waiver',
    )
    
    list_display = ('name', 'start_date', 'end_date', 'venue',
        'is_active'
    )
    
    list_filter = ('venue',)
    search_fields= ('name',)

class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'transaction', 'created_time')
    list_display = ('uuid', 'transaction', 'activated', 'created_time', 'activated_time', 'notes')
    list_filter = ('event', 'activated')
    search_fields = ['uuid', 'transaction__txn_id']
    
class WaiverAdmin(admin.ModelAdmin):
    list_display = ('part', 'name', 'signed_on')
    list_filter = ('minor', )
    search_fields = ('name', )
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Ticket)
admin.site.register(TicketType)
admin.site.register(Transaction)
#admin.site.register(Waiver, WaiverAdmin)
#admin.site.register(Coupon, CouponAdmin)

