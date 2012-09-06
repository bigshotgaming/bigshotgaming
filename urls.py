from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings
from django.contrib import admin


from pages.forms import RegistrationForm

import functools
import re

def add_remoteip(function, request):
    form = functools.partial(RegistrationForm, remote_ip=request.META['REMOTE_ADDR'])
    return function(request, form_class=form)

# This is a total hack that decorates the register view. It allows us to provide a dynamic parameter (remote IP address)
# to the registration form.
from registration.urls import urlpatterns as registration_urlpatterns
for i, rurl in enumerate(registration_urlpatterns):
    if rurl.name == 'registration_register':
        registration_urlpatterns[i]._callback = functools.partial(add_remoteip, registration_urlpatterns[i]._callback)
                
from pages.views import NewsFeed
admin.autodiscover()

sitemaps = {
}

urlpatterns = patterns('',
    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Sitemap
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    # Apps
    (r'^accounts/', include('registration.urls')),
    (r'^events/', include('events.urls')),
    (r'^seatmap/', include('seatmap.urls')),

)

# PM Extension
# if (forum_settings.PM_SUPPORT):
#     import messages.urls as messages_urls
#     for p in messages_urls.urlpatterns:
#         if p.name == 'messages_compose_to':
#             p.regex = re.compile(r'^compose/(?P<recipient>[\w\s_\-+@.\[\]\$\*]+)/$')

#     urlpatterns += patterns('',
#         (r'^forum/pm/', include(messages_urls)),
#    )

if (settings.DEBUG):
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns('',
    (r'^rss/', NewsFeed()),
    (r'^', include('pages.urls')),
)
