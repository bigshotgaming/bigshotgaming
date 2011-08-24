from django.conf.urls.defaults import *
from events.forms import RegisterForm1, RegisterForm2, RegisterForm3, RegisterWizard

urlpatterns = patterns('events.views',
    (r'^$', 'index', {}, 'events_index'),
    # fix me
    (r'^register/(\d{1})/$', RegisterWizard([RegisterForm1, RegisterForm2, RegisterForm3]), {}, 'events_register'),
)
