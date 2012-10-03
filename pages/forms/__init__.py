import re
from django import forms
from django.contrib.auth.models import User
from registration.forms import RegistrationFormUniqueEmail
from pages.forms.recaptcha import ReCaptchaField

class RegistrationForm(RegistrationFormUniqueEmail):
    '''
    Allowed UTF8 logins with space, along with a recaptcha field.
    '''

    username = forms.RegexField(regex=r'^[\w\s_\-+@.\[\]\$\*]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={'class': 'required'}),
                                label=u'username')

    def __init__(self, *args, **kwargs):
        remote_ip = kwargs.pop('remote_ip')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField(remote_ip=remote_ip)

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.widgets.Textarea)

class VolunteerForm(forms.Form):
    VOLUNTEER_CHOICES = (
        ('IT', 'IT/Infrastructure'),
        ('TA', 'Tournament Administration'),
        ('GH', 'General Help'),
        ('MS', 'Marketing & Sponsorship'),
    )
    
    your_name = forms.CharField(max_length=50)
    city = forms.CharField(max_length=30)
    comments_and_experience = forms.CharField(widget=forms.widgets.Textarea)
    cmu_student = forms.BooleanField()
    desired_position = forms.ChoiceField(choices=VOLUNTEER_CHOICES)


