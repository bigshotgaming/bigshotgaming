from django.conf.urls.defaults import *

urlpatterns = patterns('pages.views',
    (r'^reviews', 'reviews', {}, 'pages_reviews'),
    (r'^contact', 'contact', {}, 'pages_contact'),
    (r'^$', 'index', {}, 'pages_index'),
)
