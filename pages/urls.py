from django.conf.urls.defaults import *

urlpatterns = patterns('pages.views',
    (r'^reviews', 'reviews', {}, 'pages_reviews'),
    (r'^contact', 'contact', {}, 'pages_contact'),
    (r'^sponsors', 'sponsors', {}, 'pages_sponsors'),
    (r'^$', 'index', {}, 'pages_index'),
    (r"^(\d+)/$", "post"),
)
