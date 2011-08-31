from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django import forms
from django.template import RequestContext
from events.models import Event, Venue, Participant, Ticket, Coupon

class ATDForm(forms.Form):
    participant = forms.ModelChoiceField(queryset=Participant.objects.all(), required=True)
    
class ParticipantAdmin(admin.ModelAdmin):    
    def get_urls(self):
        urls = super(ParticipantAdmin, self).get_urls()
        admin_urls = patterns('', 
            url(r'^payatd/$', self.admin_site.admin_view(self.pay_atd)),
        )
        
        return admin_urls + urls
        
    def pay_atd(self, request):
        if request.method == 'POST':
            form = ATDForm(request.POST)
            if form.is_valid():
                coupon = Coupon()
                coupon.save()
                
                ticket = Ticket(participant=form.cleaned_data['participant'], coupon=coupon,)
                ticket.save()
                
                
                #form.cleaned_data['participant'].is_paid = True
                #form.cleaned_data['participant'].save()
                
                print form.cleaned_data
                #for name in form.cleaned_data['names']:
                #    import_user.delay(name, category=form.cleaned_data['category'], user=request.user)
                #self.message_user(request, 'Importing users...')
                #return redirect('admin:namelist_player_changelist')

        form = ATDForm()
        context = RequestContext(request, current_app=self.admin_site.name)
        return render_to_response('events/admin/change_form.html', {
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_add_permission': True,
            'has_delete_permission': True,
            'has_change_permission': True,
            'show_delete':True,
            'add': True,
            'change': False,
            'is_popup': False,
            'save_as': True,
            'title': 'At-The-Door Payment',
            'form': form,
            'media': self.media,
        }, context_instance=context)
    

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
    
admin.site.register(Event, EventAdmin)
admin.site.register(Venue)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Ticket)

