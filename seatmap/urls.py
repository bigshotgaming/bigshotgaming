from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'seatmap.views.seatmap_display'),
    (r'^seat/(?P<seat>\d+)/$', 'seatmap.views.seat_display'),
    (r'^admin/$', 'seatmap.views.seatmap_admin'),
    (r'^admin/seat/(?P<seat>\d+)/$', 'seatmap.views.seat_admin'),
    (r'^admin/seat/create/$', 'seatmap.views.seat_create'),
    (r'^admin/table/create/$', 'seatmap.views.table_create'),
    (r'^data/$', 'seatmap.views.seatmap_data'),
)
