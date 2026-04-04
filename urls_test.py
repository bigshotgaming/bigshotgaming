"""Minimal URL configuration for tests (no allauth, registration, etc.)."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf import settings

from pages.views import NewsFeed


def _stub_view(request, *args, **kwargs):
    return HttpResponse('stub')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Stub URLs for allauth names referenced in templates
    path('accounts/signup/', _stub_view, name='account_signup'),
    path('accounts/login/allauth/', _stub_view, name='account_login'),
    path('accounts/password/reset/', _stub_view, name='account_reset_password'),
    path('accounts/profile/', _stub_view, name='account_profile'),
    # App URLs
    path('events/', include('events.urls')),
    path('seatmap/', include('seatmap.urls')),
    path('tournaments/', include('tournaments.urls')),
    path('schedule/', include('schedule.urls')),
    path('rss/', NewsFeed()),
    path('', include('pages.urls')),
]
