from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'seatmap.views.seatmap_display'),
    (r'^seat/(?P<x>\d+)/(?P<y>\d+)/$', 'seatmap.views.seat_display'),
)
