from django.contrib.admin import site
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from djangobb_forum.admin import UserAdmin
from django import forms

class ExtendedChangeForm(UserChangeForm):
    username = forms.RegexField(regex=r'^[\w\s_\-+@.\[\]]+$',
                                max_length=30,
                                label=u'Username')


class ExtendedCreationForm(UserCreationForm):
    username = forms.RegexField(regex=r'^[\w\s_\-+@.\[\]]+$',
                                max_length=30,
                                label=u'Username')
                                
class ExtendedUserAdmin(UserAdmin):
    form = ExtendedChangeForm
    add_form = ExtendedCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
site.unregister(User)
site.register(User, ExtendedUserAdmin)
