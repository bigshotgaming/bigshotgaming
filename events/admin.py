from django.http import HttpResponse
from django.contrib import admin
from events.models import Event, Venue, Participant, Coupon

def mark_as_paid(modeladmin, request, queryset):
    for participant in queryset:
        participant.coupon = Coupon()
        participant.coupon.activate()
        participant.save()
mark_as_paid.short_description = "Mark selected participants as paid"

class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('signup_time',)
    list_display = ('user', 'event', 'coupon', 'signup_time', 'checkin_time')
    list_filter = ('event', 'checked_in')
    actions = [mark_as_paid]
    
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
    
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
admin.site.register(Participant, ParticipantAdmin)

admin.site.register(Coupon, CouponAdmin)

