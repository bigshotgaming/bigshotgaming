from django.urls import path, re_path
import pages.views as views

urlpatterns = [
    re_path(r'^reviews', views.reviews, name='pages_reviews'),
    re_path(r'^contact', views.contact, name='pages_contact'),
    re_path(r'^volunteer', views.volunteer, name='pages_volunteer'),
    re_path(r'^sponsors', views.sponsors, name='pages_sponsors'),
    path('', views.index, name='pages_index'),
    re_path(r'^(\d+)/$', views.post, name='pages_post'),
]

