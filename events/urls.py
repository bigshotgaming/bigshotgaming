from django.conf.urls.defaults import *

urlpatterns = patterns('events.views',
    (r'^$', 'index', {}, 'events_index'),
)
