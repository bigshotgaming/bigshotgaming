from django.conf.urls.defaults import *

urlpatterns = patterns('pages.views',
    (r'^$', 'index', {}, 'pages_index'),
)
