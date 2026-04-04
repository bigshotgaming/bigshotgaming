from django.urls import path, re_path
import tournaments.views as views

urlpatterns = [
    path('', views.index, name='tournaments_index'),
    re_path(r'^tournament/(\d+)/$', views.tournament, name='tournaments_tournament'),
    re_path(r'^team/(\d+)/$', views.team, name='tournaments_team'),
]
