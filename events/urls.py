from django.urls import path, re_path, include
import events.views as views

urlpatterns = [
    path('', views.index, name='events_index'),
    re_path(r'^register/(\d+)/$', views.register, name='events_register'),
    re_path(r'^participants/(\d+)/', views.participants, name='events_participants'),
    path('payment/', views.payment, name='events_payment'),
    re_path(r'^activate/(\d+)/([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/', views.activate, name='events_activate'),
    re_path(r'^ppnotification', include('paypal.standard.ipn.urls')),
    re_path(r'^waiver/(\d+)', views.waiver, name='events_waiver'),
    path('waiver/sign/', views.waiver_sign, name='events_waiver_sign'),
    re_path(r'^admin/events/(?P<event_id>\d+)/name_badges_pdf/$', views.name_badges_pdf),
    re_path(r'^admin/events/(?P<event_id>\d+)/registration_history/$', views.registration_history),
]

