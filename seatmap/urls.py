from django.urls import path, re_path
import seatmap.views as views

urlpatterns = [
    path('', views.seatmap_display, name='seatmap_display'),
    re_path(r'^seat/(?P<seat>\d+)/$', views.seat_display, name='seatmap_seat_display'),
    path('admin/', views.seatmap_admin, name='seatmap_admin'),
    re_path(r'^admin/seat/(?P<seat>\d+)/$', views.seat_admin, name='seatmap_seat_admin'),
    path('data/', views.seatmap_data, name='seatmap_data'),
    path('users/', views.seatmap_user, name='seatmap_user'),
    path('sitdown/', views.seatmap_sitdown, name='seatmap_sitdown'),
    path('admin/seat/create/', views.seat_create, name='seatmap_seat_create'),
    path('admin/table/create/', views.table_create, name='seatmap_table_create'),
    path('admin/seatmap/save/', views.seatmap_save, name='seatmap_save'),
]

