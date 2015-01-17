from django.conf.urls import patterns, url, include

urlpatterns = patterns('pages.views',
    (r'^reviews', 'reviews', {}, 'pages_reviews'),
    (r'^contact', 'contact', {}, 'pages_contact'),
    (r'^volunteer', 'volunteer', {}, 'pages_volunteer'),
    (r'^sponsors', 'sponsors', {}, 'pages_sponsors'),
    (r'^$', 'index', {}, 'pages_index'),
    (r"^(\d+)/$", "post"),
)
