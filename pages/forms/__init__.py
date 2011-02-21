import re
from django import forms
from registration.forms import RegistrationFormUniqueEmail
from pages.forms.recaptcha import ReCaptchaField

class RegistrationForm(RegistrationFormUniqueEmail):
    '''
    Allowed UTF8 logins with space, along with a recaptcha field.
    '''

    def __init__(self, *args, **kwargs):
        remote_ip = kwargs.pop('remote_ip')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].regex = re.compile(r"^[\w\s-]+$", re.UNICODE)
        self.fields['captcha'] = ReCaptchaField(remote_ip=remote_ip)
