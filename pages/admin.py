from django.contrib import admin
from django.core import mail
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
        # yes, as currently written, this only supports one active event
        from events.models import Event, Participant
        connection = mail.get_connection()
        connection.open()
        for obj in queryset:
            email = mail.EmailMessage(
                subject=obj.title,
                body=obj.body,
                to=[participant.user.email for participant in Participant.objects.filter(event__is_active=True)],
                connection=connection,
            )
            email.preserve_recipients = False
            email.send()
        connection.close()

    email_post_participants.short_description = "Email all participants for the current event"

    def email_post_all(self, request, queryset):
        connection = mail.get_connection()
        connection.open()
        for obj in queryset:
            email = mail.EmailMessage(
                subject=obj.title,
                body=obj.body,
                to=[u.email for u in User.objects.filter(is_active=True)],
                connection=connection
            )
            email.preserve_recipients = False
            email.send()
        connection.close()

    email_post_all.short_description = "Email all active users"

admin.site.unregister(User)   
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Post, PostAdmin)