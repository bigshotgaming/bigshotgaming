from django.urls import path
import schedule.views as views

urlpatterns = [
    path('', views.index, name='schedule_index'),
]
