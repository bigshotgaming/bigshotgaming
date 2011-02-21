from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.conf import settings
import urllib2, urllib

class ReCaptcha(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        widget = u"""
        <script type="text/javascript">
        var RecaptchaOptions = {{}};
        RecaptchaOptions.theme = 'custom';
        RecaptchaOptions.custom_theme_widget = 'recaptcha_widget';
        </script>
        <div id="recaptcha_widget" style="display:none">

           <div id="recaptcha_image"></div>
           <div class="recaptcha_only_if_incorrect_sol" style="color:red">Incorrect please try again</div>

           <span class="recaptcha_only_if_image">Enter the words above:</span>
           <span class="recaptcha_only_if_audio">Enter the numbers you hear:</span>

           <input type="text" id="recaptcha_response_field" name="recaptcha_response_field" />

           <div><a href="javascript:Recaptcha.reload()">Get another CAPTCHA</a></div>
           <div class="recaptcha_only_if_image"><a href="javascript:Recaptcha.switch_type('audio')">Get an audio CAPTCHA</a></div>
           <div class="recaptcha_only_if_audio"><a href="javascript:Recaptcha.switch_type('image')">Get an image CAPTCHA</a></div>

           <div><a href="javascript:Recaptcha.showhelp()">Help</a></div>

         </div>

         <script type="text/javascript"
            src="http://www.google.com/recaptcha/api/challenge?k={public_key}">
         </script>
         <noscript>
           <iframe src="http://www.google.com/recaptcha/api/noscript?k={public_key}"
                height="300" width="500" frameborder="0"></iframe><br>
           <textarea name="recaptcha_challenge_field" rows="3" cols="40">
           </textarea>
           <input type="hidden" name="recaptcha_response_field"
                value="manual_challenge">
         </noscript>
        """
        return mark_safe(widget.format(public_key=settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), 
        data.get(self.recaptcha_response_name, None)]


class ReCaptchaField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': u'Invalid captcha'
    }

    def __init__(self, remote_ip, *args, **kwargs):
        self.widget = ReCaptcha
        self.required = True
        self.remote_ip = remote_ip
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        
        check_captcha = self.verify_captcha(recaptcha_challenge_value, 
        recaptcha_response_value)
        if not check_captcha:
            raise forms.util.ValidationError(u'Incorrect captcha value.')
            return values[0]
            
    def verify_captcha(self, challenge, response):
        url = 'http://www.google.com/recaptcha/api/verify'
        
        values = {
            'privatekey': settings.RECAPTCHA_PRIVATE_KEY,
            'remoteip': self.remote_ip,
            'challenge': challenge,
            'response': response,
        }
        
        request = urllib2.urlopen(url, data=urllib.urlencode(values))
        result = request.read().split('\n')
        
        return result[0] == 'true'
