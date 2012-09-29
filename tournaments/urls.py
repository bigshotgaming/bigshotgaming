from django.conf.urls.defaults import *
# from events.forms import RegisterForm1, RegisterForm2, RegisterForm3, RegisterWizard



urlpatterns = patterns('tournaments.views',
    (r'^$', 'index', {}, 'tournaments_index'),
    (r"^tournament/(\d+)/$", 'tournament', {}, 'tournaments_tournament'),
    (r"^team/(\d+)/$", 'team', {}, 'tournaments_team'),
)