from django.conf.urls.defaults import *

urlpatterns = patterns('pooling.views',
    (r'^$', 'index', {}, 'pooling_index'),
    (r"^cars/$", 'cars', {}, 'pooling_cars'),
)