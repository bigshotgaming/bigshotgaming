from django.http import HttpResponse
from django.contrib import admin
from events.models import Event, Venue, Participant, Coupon

def mark_as_paid(modeladmin, request, queryset):
    for participant in queryset:
        participant.coupon = Coupon(event=Event.objects.get(is_active=True))
        participant.coupon.activate()
        participant.save()
mark_as_paid.short_description = "Mark selected participants as paid"

class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('signup_time',)
    list_display = ('user', 'event', 'coupon', 'signup_time', 'checkin_time', 'user_has_seat')
    list_filter = ('event', 'checked_in')
    search_fields = ['user__username', 'coupon__uuid']
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
        'participant_limit', 'description', 'is_active',
        'prepay_price', 'atd_price'
    )
    
    list_display = ('name', 'start_date', 'end_date', 'venue',
        'participant_limit', 'is_active'
    )
    
    list_filter = ('venue',)
    search_fields= ('name',)

class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'transaction', 'created_time')
    list_display = ('uuid', 'transaction', 'activated', 'created_time', 'activated_time')
    list_filter = ('event', 'activated')
    search_fields = ['uuid', 'transaction__txn_id']
    
class WaiverAdmin(admin.ModelAdmin):
    list_display = ('part', 'name', 'alias', 'signed_on')
    list_filter = ('minor', )
    search_fields = ('name', 'alias')
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Waiver, WaiverAdmin)
admin.site.register(Coupon, CouponAdmin)

