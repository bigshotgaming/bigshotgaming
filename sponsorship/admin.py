from sponsorship.models import Sponsor
from sponsorship.models import Prize
from django.contrib import admin
from django import forms

class PrizeAdminForm(forms.ModelForm):
    class Meta:
        model = Prize
     
    def clean_sponsor(self):
        if self.cleaned_data['sponsor'].status != 'CONF':
            raise forms.ValidationError("Sponsor must be confirmed before prizes can be added.")
        return self.cleaned_data['sponsor']

class SponsorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contact Information', {'fields': ['name', 'contact_name',
            'contact_email', 'contact_phone', 'status']}),
            
        ('Other Information',   { 'fields': ['lan_rep', 'notes']}),
    ]
    
    list_display = ('name', 'status', 'lan_rep')
    list_filter = ('status',)
    search_fields = ('name',)

class PrizeAdmin(admin.ModelAdmin):
    form = PrizeAdminForm
    fields = ('sponsor', 'name', 'description')
    list_display = ('name', 'sponsor')
    search_fields = ('name', 'sponsor')

    
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(Prize, PrizeAdmin)