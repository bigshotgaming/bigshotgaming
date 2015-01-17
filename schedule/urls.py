from django.conf.urls import patterns, url, include
# from events.forms import RegisterForm1, RegisterForm2, RegisterForm3, RegisterWizard



urlpatterns = patterns('schedule.views',
    (r'^$', 'index', {}, 'schedule_index'),
)