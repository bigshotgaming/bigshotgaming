from django.conf.urls.defaults import *
# from events.forms import RegisterForm1, RegisterForm2, RegisterForm3, RegisterWizard

# initial = {
#     3: {
#         "business": "wiede1_1297892766_biz@cmich.edu",
#         "amount": "15.00",
#         "item_name": "thing",
#         "invoice": "9010",
#         "notify_url": "http://24.236.128.202:8000/ticketing/ppnotify/",
#         "return_url": "http://bsg.tomthebomb.net/registration/thanks/",
#         "cancel_return": "http://bsg.tomthebomb.net/registration/thanks/",
#     }
# }


urlpatterns = patterns('events.views',
    (r'^$', 'index', {}, 'events_index'),
    # fix me
    # 
    (r'^register/(\d+)/$', 'register', {}, 'events_register'),
    (r'^payment/', 'payment', {}, 'events_payment'),
    #(r'^payment/(?P<ticketID>\w+)/', 'payment', {}, 'events_payment'),
    (r'^activate/(\d+)/([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/', 'activate', {}, 'events_activate'),
    (r'^ppnotification', include('paypal.standard.ipn.urls')), 
    #(r'^register/(\d{1})/$', RegisterWizard([RegisterForm1, RegisterForm2, RegisterForm3], initial=initial), {}, 'events_register'),
)
