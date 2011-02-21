from django import forms
from django.contrib.auth.models import User

class ContactForm(forms.Form):
    staff_member = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True))
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.widgets.Textarea)
