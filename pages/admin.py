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

admin.site.unregister(User)   
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Post, PostAdmin)