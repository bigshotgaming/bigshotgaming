from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from pages.models import Post

class ExtendedChangeForm(UserChangeForm):
    username = forms.RegexField(regex=r'^[\w\s_\-+@.\[\]\$\*]+$',
                                max_length=30,
                                label=u'Username')


class ExtendedCreationForm(UserCreationForm):
    username = forms.RegexField(regex=r'^[\w\s_\-+@.\[\]\$\*]+$',
                                max_length=30,
                                label=u'Username')
                                
class ExtendedUserAdmin(UserAdmin):
    form = ExtendedChangeForm
    add_form = ExtendedCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

class PostAdmin(admin.ModelAdmin):
    search_fields = ['title']
    actions = ['email_post_participants', 'email_post_all']

    def email_post_participants(self, request, queryset):
        from events.models import Event, Participant
        from django.core.mail import send_mass_mail
        participants = Participant.objects.filter(event__is_active=True)
        for obj in queryset:
            for participant in participants:
                fr_email = 'Big Shot Gaming <bigshot@bigshotgaming.com>'
                dt = (obj.title, obj.body, fr_email, [participant.user.email])
                send_mass_mail((dt,))

    email_post_participants.short_description = "Email all participants for the current event"

    def email_post_all(self, request, queryset):
        from django.core.mail import send_mass_mail
        users = User.objects.all()
        for obj in queryset:
            for user in users:
                fr_email = 'Big Shot Gaming <bigshot@bigshotgaming.com>'
                dt = (obj.title, obj.body, fr_email, [user.email])
                send_mass_mail((dt,))

    email_post_all.short_description = "Email all users"

admin.site.unregister(User)   
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Post, PostAdmin)