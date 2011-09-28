from sponsorship.models import Sponsor, Prize, EventSponsor
from events.models import Event
from django.contrib import admin
from django.contrib.auth.models import User 
from django import forms
import datetime

class PrizeAdminForm(forms.ModelForm):
    class Meta:
        model = Prize
    
    def clean_event(self):
        print self.cleaned_data
        if self.cleaned_data['eventsponsor__event'].end_date < datetime.datetime.now():
            raise forms.ValidationError("Prizes cannot be added to events in the past.")
        return self.cleaned_data['eventsponsor__event']
        
class EventSponsorInline(admin.TabularInline):
    model = EventSponsor
    extra = 0
    template = 'sponsor_tabular.html'
    verbose_name = 'Sponsored Event'
    verbose_name_plural = 'Sponsored Events'

            
class SponsorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contact Information', {'fields': ['name', 'contact_name',
            'contact_email', 'contact_phone', 'contact_form_url',]}),
            
        ('Other Information',   { 'fields': ['lan_rep', 'notes', 'banner_url', 'banner',
            'featured_sponsor', 'featured_banner',]}),

    ]
    
    list_display = ('name', 'lan_rep',)
    list_filter = ('lan_rep', 'eventsponsor__status', 'eventsponsor__event')
    search_fields = ('name',)
    inlines = (EventSponsorInline,)
    actions = ['reset_sponsors']
    
    # def set_followup(self, request, queryset):
    #     queryset.update(status="r")
    # set_followup.short_description = "Set sponsors to Follow-Up Required"
    # 
    def reset_sponsors(self, request, queryset):
        for obj in queryset:
            es = EventSponsor.objects.get_or_create(sponsor=obj, event=Event.objects.filter(start_date__gt=datetime.datetime.today()).order_by('start_date')[0], status='n')
        
    reset_sponsors.short_description = "Reset sponsors for new event"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs): 
        if db_field.name == 'lan_rep': 
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
    list_filter = ('eventsponsor__event',)
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
