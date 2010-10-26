from sponsorship.models import Sponsor
from sponsorship.models import Prize
from sponsorship.models import EventSponsor
from events.models import Event
from django.contrib import admin
from django.contrib.auth.models import User 
from django import forms
import datetime

class PrizeAdminForm(forms.ModelForm):
    class Meta:
        model = Prize
    
    def clean_event(self):
        if self.cleaned_data['event'].end_date < datetime.datetime.now():
            raise forms.ValidationError("Prizes cannot be added to events in the past.")
        return self.cleaned_data['event']
        
class EventSponsorInline(admin.TabularInline):
    model = EventSponsor
    extra = 0
    template = 'sponsor_tabular.html'
    verbose_name = 'Sponsored Event'
    verbose_name_plural = 'Sponsored Events'

            
class SponsorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contact Information', {'fields': ['name', 'contact_name',
            'contact_email', 'contact_phone']}),
            
        ('Other Information',   { 'fields': ['lan_rep', 'notes']}),
    ]
    
    list_display = ('name', 'lan_rep', 'get_upcoming_event_status')
    list_filter = ('lan_rep',)
    search_fields = ('name',)
    inlines = (EventSponsorInline,)
    #actions = ['set_followup', 'reset_sponsors']
    
    # def set_followup(self, request, queryset):
    #     queryset.update(status="r")
    # set_followup.short_description = "Set sponsors to Follow-Up Required"
    # 
    # def reset_sponsors(self, request, queryset):
    #     queryset.update(status="n")
    # reset_sponsors.short_description = "Reset sponsors for new event"
    
    def get_upcoming_event_status(self, obj):
        edate = Event.objects.filter(start_date__gt=datetime.datetime.today()).order_by('start_date')[0]
        curobj = EventSponsor.objects.filter(event=edate, sponsor=obj)
        if curobj.count() > 0:
            return curobj[0].get_status_display()
        return 'Not Contacted'

    get_upcoming_event_status.short_description = 'Upcoming Event Status'
        
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs): 
        if db_field.name == 'lan_rep': 
            kwargs['queryset'] = User.objects.filter(is_staff=True) 
            kwargs['initial'] = request.user.id 
            return db_field.formfield(**kwargs)
        return super(SponsorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #      if db_field.name == "event":
    #          kwargs['queryset'] = Sponsor.objects.filter(event__start_date__gt = datetime.datetime.now())
    #          kwargs['initial'] = req
    #          return db_field.formfield(**kwargs)
    #      return super(SponsorAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

class PrizeAdmin(admin.ModelAdmin):
    form = PrizeAdminForm
    fields = ('name', 'description', 'raffle_prize', 'eventsponsor')
    list_display = ('name', 'get_sponsor_name', 'get_event_name')
    list_filter = ()
    search_fields = ('name',)
    
#    inlines = (EventSponsorInline,)
    
    # def formfield_for_foreignkey(self, db_field, request, **kwargs): 
    #     if db_field.name == 'event': 
    #         kwargs['queryset'] = Event.objects.all()
    #         kwargs['initial'] = request.user.id 
    #         return db_field.formfield(**kwargs)
    #     return super(SponsorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(Prize, PrizeAdmin)