from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^sponsorship/', include('sponsorship.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^signup/', 'attendeereg.views.signup'),
)